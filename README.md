# ListService - Serverless REST API

A serverless application for managing lists of strings with head and tail operations, built on AWS using Terraform.

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [API Reference](#api-reference)
- [AWS Setup](#aws-setup)
- [Deployment](#deployment)
- [Local Development](#local-development)
- [Monitoring](#monitoring)

---

## Quick Start

### Live Deployment

A live instance of this API is available at:

```
https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api
```

You can test it directly without deploying your own instance!

### Test the Live API

```bash
# Set the API endpoint
export API_ENDPOINT="https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api"

# Create a new list
curl -X POST "${API_ENDPOINT}/lists" \
  -H "Content-Type: application/json" \
  -d '{"items": ["apple", "banana", "cherry", "date", "elderberry"]}'

# Response includes generated list_id:
# {"list_id": "4d035553-7929-44f8-882f-df1ca0e486fe", ...}

# Get first 3 items
curl "${API_ENDPOINT}/lists/4d035553-7929-44f8-882f-df1ca0e486fe/head?n=3"

# Get last 3 items
curl "${API_ENDPOINT}/lists/4d035553-7929-44f8-882f-df1ca0e486fe/tail?n=3"
```

### Deploy Your Own Instance

#### Prerequisites

- AWS Account
- [AWS CLI](https://aws.amazon.com/cli/) configured
- [Terraform](https://www.terraform.io/downloads) >= 1.0
- Python 3.11+

#### Deploy in 3 Steps

```bash
# 1. Configure AWS CLI
aws configure

# 2. Deploy infrastructure
cd terraform
terraform init
terraform apply

# 3. Get your API endpoint
terraform output api_endpoint
```

---

## Architecture

### Component Diagram

```
Client → API Gateway → Lambda Function → DynamoDB
                            ↓
                       CloudWatch
```

### AWS Services

| Service         | Purpose                | Configuration                |
| --------------- | ---------------------- | ---------------------------- |
| **API Gateway** | REST API endpoint      | Regional, throttling enabled |
| **Lambda**      | Serverless compute     | Python 3.11, 256MB, 30s      |
| **DynamoDB**    | NoSQL data store       | On-demand, encrypted         |
| **CloudWatch**  | Logs, metrics, alarms  | 30-day retention             |
| **IAM**         | Security & permissions | Least privilege              |

### Key Features

✅ **Serverless** - No servers to manage, auto-scales  
✅ **Cost-Efficient** - Pay per use, no idle costs  
✅ **Secure** - Encryption, IAM, HTTPS, input validation  
✅ **Observable** - Structured logs, metrics, alarms  
✅ **Infrastructure as Code** - Terraform-managed

---

## API Reference

### Base URL

**Live Deployment:**

```
https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api
```

**After your own deployment, your base URL will be:**

```
https://{api-id}.execute-api.{region}.amazonaws.com/api
```

### Endpoints

#### 1. Create List (Auto-Generated ID)

```http
POST /lists
Content-Type: application/json

{
  "items": ["string1", "string2", "string3"]
}
```

**Response (201 Created):**

```json
{
  "list_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": ["string1", "string2", "string3"],
  "count": 3,
  "created_at": "2025-11-10T12:00:00Z",
  "updated_at": "2025-11-10T12:00:00Z"
}
```

#### 2. Get All Lists

```http
GET /lists
```

**Response (200 OK):**

```json
{
  "lists": [
    {
      "list_id": "550e8400-e29b-41d4-a716-446655440000",
      "items": ["string1", "string2"],
      "count": 2,
      "created_at": "2025-11-10T12:00:00Z",
      "updated_at": "2025-11-10T12:00:00Z"
    }
  ],
  "count": 1
}
```

#### 3. Get Single List

```http
GET /lists/{list_id}
```

**Response (200 OK):**

```json
{
  "list_id": "550e8400-e29b-41d4-a716-446655440000",
  "items": ["string1", "string2", "string3"],
  "count": 3,
  "created_at": "2025-11-10T12:00:00Z",
  "updated_at": "2025-11-10T12:00:00Z"
}
```

#### 4. Update List (Must Exist)

```http
PUT /lists/{list_id}
Content-Type: application/json

{
  "items": ["new1", "new2", "new3"]
}
```

**Response (200 OK):** Updated list data  
**Response (404 Not Found):** If list doesn't exist

#### 5. Delete List

```http
DELETE /lists/{list_id}
```

**Response (204 No Content):** Empty body  
**Response (404 Not Found):** If list doesn't exist

#### 6. Get Head (First N Items)

```http
GET /lists/{list_id}/head?n=5
```

**Query Parameters:**

- `n` (optional): Number of items (default: 10, max: 100)

**Response (200 OK):**

```json
{
  "list_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation": "head",
  "items": ["string1", "string2", "string3"],
  "count": 3,
  "total_count": 10
}
```

#### 7. Get Tail (Last N Items)

```http
GET /lists/{list_id}/tail?n=5
```

**Query Parameters:**

- `n` (optional): Number of items (default: 10, max: 100)

**Response (200 OK):**

```json
{
  "list_id": "550e8400-e29b-41d4-a716-446655440000",
  "operation": "tail",
  "items": ["string8", "string9", "string10"],
  "count": 3,
  "total_count": 10
}
```

### Error Responses

#### 404 Not Found

```json
{
  "error": "NotFound",
  "message": "List 'my-list' not found"
}
```

#### 400 Bad Request

```json
{
  "error": "BadRequest",
  "message": "Invalid parameter: n must be between 1 and 100"
}
```

#### 500 Internal Server Error

```json
{
  "error": "InternalServerError",
  "message": "An unexpected error occurred"
}
```

---

## AWS Setup

### Step 1: Create IAM User

1. Go to AWS Console → IAM → Users → Create user
2. User name: `terraform-operator`
3. Select "Attach policies directly"
4. Attach policy: `AdministratorAccess` (or create a custom policy with specific permissions)

### Step 2: Create Access Key

1. Click on the created user
2. Go to "Security credentials" tab
3. Click "Create access key"
4. Choose "Command Line Interface (CLI)"
5. Save the Access Key ID and Secret Access Key

### Step 3: Configure AWS CLI Profile

```bash
aws configure --profile terraform-operator
```

Enter the credentials from Step 2.

### Step 4: Use the Profile

Update `terraform/variables.tf`:

```hcl
variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "terraform-operator"
}
```

### Verify Setup

```bash
aws sts get-caller-identity --profile terraform-operator
```

---

## Deployment

### Initial Deployment

```bash
# Navigate to terraform directory
cd terraform

# Initialize Terraform (first time only)
terraform init

# Review what will be created
terraform plan

# Deploy infrastructure
terraform apply

# Get the API endpoint
terraform output api_endpoint
```

**Deployment time:** ~2-3 minutes

### Configuration Options

Available variables (see `terraform/variables.tf`):

- `aws_profile` - AWS CLI profile name
- `aws_region` - AWS region
- `lambda_memory_size` - Lambda memory in MB (default: 256)
- `lambda_timeout` - Lambda timeout in seconds (default: 30)
- `log_retention_days` - CloudWatch log retention (default: 30)

### Updating the Application

After making changes to code or infrastructure:

```bash
cd terraform
terraform apply
```

Terraform will detect changes and update only what's needed.

### Rollback

If you need to rollback:

```bash
# View state history
terraform state list

# Or redeploy from Git
git checkout <previous-commit>
cd terraform
terraform apply
```

### Cleanup

To destroy all resources and stop incurring costs:

```bash
cd terraform
terraform destroy
# Type 'yes' when prompted
```

**Warning:** This permanently deletes all data and resources.

---

## Local Development

### Setup

```bash
# Install dependencies
make install

# Or manually:
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Environment Configuration

Create a `.env` file at the project root to configure the API endpoint for integration tests:

```bash
# .env
API_ENDPOINT=https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api
```

This file is used by the integration tests to know which API to test against. You can use the live deployment endpoint or your own deployment endpoint.

### Available Make Commands

```bash
make help       # Show all available commands
make install    # Install dependencies
make test       # Run unit tests
make test-cov   # Run tests with coverage report
make test-int   # Run integration tests (requires deployed API)
make format     # Format code with black
make clean      # Clean temporary files
```

### Running Tests

#### Unit Tests

```bash
make test

# Or manually:
pytest tests/unit/ -v
```

#### Integration Tests

Requires deployed infrastructure. Make sure you have a `.env` file with the API endpoint:

```bash
# Create .env file (if not exists)
echo "API_ENDPOINT=https://cfuebpkgu1.execute-api.eu-north-1.amazonaws.com/api" > .env

# Load environment variables
source .env

# Run integration tests
make test-int

# Or manually:
pytest tests/integration/ -v
```

#### Test Coverage

```bash
make test-cov

# View HTML report
open htmlcov/index.html
```

#### Load Testing

```bash
python tests/load/load_test.py --requests 1000 --concurrent 10
```

### Code Formatting

```bash
make format

# Or manually:
black src tests
```

### Project Structure

```
list-service/
├── README.md
├── Makefile
├── .env                        # Environment variables (API_ENDPOINT)
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── src/
│   ├── lambda_function.py      # Main Lambda handler
│   ├── list_operations.py      # Business logic
│   ├── validators.py           # Input validation
│   └── utils.py                # Utility functions
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── load/                   # Load tests
└── terraform/
    ├── main.tf                 # Main infrastructure
    ├── variables.tf            # Input variables
    ├── outputs.tf              # Output values
    ├── lambda.tf               # Lambda configuration
    ├── api_gateway.tf          # API Gateway configuration
    ├── dynamodb.tf             # DynamoDB configuration
    └── cloudwatch.tf           # Monitoring configuration
```

---

## Monitoring

### CloudWatch Dashboard

Access the dashboard:

1. Go to AWS Console → CloudWatch → Dashboards
2. Select `list-service-dashboard`

### CloudWatch Alarms

Configured alarms:

| Alarm              | Threshold        | Action |
| ------------------ | ---------------- | ------ |
| Lambda Errors      | >5 in 5 minutes  | Alert  |
| Lambda Throttles   | >10 in 5 minutes | Alert  |
| DynamoDB Throttles | >10 in 5 minutes | Alert  |

View alarms:

```bash
aws cloudwatch describe-alarms --alarm-name-prefix "list-service"
```

### Key Metrics

**Lambda Metrics:**

- Invocations
- Errors
- Duration
- Throttles
- Concurrent executions

**API Gateway Metrics:**

- Request count
- 4XX/5XX errors
- Latency (p50, p95, p99)

**DynamoDB Metrics:**

- Read/Write capacity units
- Throttled requests
- Item count

**Custom Metrics:**

- Operation count (head, tail, create, update, delete)
- Success rate

## Performance

### Latency Characteristics

| Metric            | Cold Start | Warm Start |
| ----------------- | ---------- | ---------- |
| Lambda Init       | ~100-200ms | ~10-50ms   |
| DynamoDB Query    | ~5-20ms    | ~5-20ms    |
| API Gateway       | ~10-20ms   | ~10-20ms   |
| **Total Latency** | ~125-290ms | ~25-90ms   |

### Throughput Limits

- **API Gateway**: 10,000 req/sec (default, can be increased)
- **Lambda**: 1,000 concurrent executions (default, can be increased)
- **DynamoDB**: Auto-scales with on-demand mode

### Scalability

- ✅ Horizontal scaling: Automatic
- ✅ Vertical scaling: Configurable (Lambda memory)
- ✅ Regional deployment: Single region (multi-region ready)

---

## Future Enhancements

- [ ] Authentication & Authorization
- [ ] Rate limiting
- [ ] Pagination for very large lists
- [ ] CI/CD automation (e.g., GitHub Actions)
- [ ] API Gateway caching for frequently accessed data
