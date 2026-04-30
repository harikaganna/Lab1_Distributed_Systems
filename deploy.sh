#!/bin/bash
set -e

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=${AWS_REGION:-us-west-2}
ECR_URL="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com"

echo "=== ECR: $ECR_URL ==="
echo ""

# 1. Login to ECR
echo ">>> Logging into ECR..."
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URL

# 2. Build and push all images
echo ">>> Building and pushing images..."

cd "$(dirname "$0")"

for svc in user restaurant review favourites; do
  echo "  Building $svc-service..."
  docker build --platform linux/amd64 -t $ECR_URL/yelp/$svc-service:latest -f backend/Dockerfile.$svc backend/
  docker push $ECR_URL/yelp/$svc-service:latest
done

for w in review-worker restaurant-worker user-worker; do
  echo "  Building $w..."
  docker build --platform linux/amd64 -t $ECR_URL/yelp/$w:latest -f backend/Dockerfile.$w backend/
  docker push $ECR_URL/yelp/$w:latest
done

echo "  Building seed..."
docker build --platform linux/amd64 -t $ECR_URL/yelp/seed:latest -f backend/Dockerfile.seed backend/
docker push $ECR_URL/yelp/seed:latest

echo "  Building ai-service..."
docker build --platform linux/amd64 -t $ECR_URL/yelp/ai-service:latest -f backend/Dockerfile.ai backend/
docker push $ECR_URL/yelp/ai-service:latest

echo "  Building frontend..."
docker build --platform linux/amd64 -t $ECR_URL/yelp/frontend:latest frontend/
docker push $ECR_URL/yelp/frontend:latest

# 3. Update K8s manifests with ECR URLs and apply
echo ""
echo ">>> Deploying to Kubernetes..."

# Create temp dir for processed manifests
TMPDIR=$(mktemp -d)
for f in k8s/*.yaml; do
  sed "s|REPLACE_ECR_URL|$ECR_URL|g" "$f" > "$TMPDIR/$(basename $f)"
done

kubectl apply -f "$TMPDIR/namespace.yaml"
kubectl apply -f "$TMPDIR/config.yaml"

# Apply secrets from the gitignored secrets.yaml (never committed to git)
if [ -f "k8s/secrets.yaml" ]; then
  kubectl apply -f "k8s/secrets.yaml"
else
  echo "ERROR: k8s/secrets.yaml not found."
  echo "Copy k8s/secrets.yaml.example to k8s/secrets.yaml and fill in your keys."
  exit 1
fi

kubectl apply -f "$TMPDIR/mongodb.yaml"
kubectl apply -f "$TMPDIR/kafka.yaml"

echo ">>> Waiting for MongoDB and Kafka to be ready..."
kubectl wait --for=condition=ready pod -l app=mongodb -n yelp --timeout=120s
kubectl wait --for=condition=ready pod -l app=kafka -n yelp --timeout=120s

kubectl apply -f "$TMPDIR/seed-job.yaml"
echo ">>> Waiting for seed job to complete..."
kubectl wait --for=condition=complete job/seed-db -n yelp --timeout=60s

kubectl apply -f "$TMPDIR/user-service.yaml"
kubectl apply -f "$TMPDIR/restaurant-service.yaml"
kubectl apply -f "$TMPDIR/review-service.yaml"
kubectl apply -f "$TMPDIR/favourites-service.yaml"
kubectl apply -f "$TMPDIR/uploads-pvc.yaml"
kubectl apply -f "$TMPDIR/workers.yaml"
kubectl apply -f "$TMPDIR/ai-service.yaml"
kubectl apply -f "$TMPDIR/frontend.yaml"

rm -rf "$TMPDIR"

echo ""
echo ">>> Deployment complete! Checking status..."
kubectl get pods -n yelp
echo ""
kubectl get services -n yelp
echo ""
echo ">>> Frontend URL:"
kubectl get svc frontend -n yelp -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "(LoadBalancer pending...)"
echo ""
echo ">>> Run 'kubectl get svc frontend -n yelp' to get the external URL once ready."
