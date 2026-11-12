# AWS Deployment Guide

**Target AWS Region**: `ap-southeast-2` (Asia Pacific - Sydney)

> [!IMPORTANT]
> **DEPLOYMENT STATUS NOTICE**: No AWS cloud resources have been automatically created or billed. All instructions, CloudFormation references, Nginx files, and deployment automation scripts are configured in this directory ready for execution upon explicit user approval.

---

## 1. Cloud Architecture Overview

```
End Users (HTTPS :443)
       │
       ▼
   AWS EC2 (Ubuntu 22.04 LTS - Web & App Tier)
   ┌─────────────────────────────────────────────────────────┐
   │ Nginx (Reverse Proxy & Static Server)                   │
   │   ├── Port 443 -> /var/www/helpdesk/frontend/dist       │
   │   └── Proxy /api/* -> Gunicorn (127.0.0.1:8000)         │
   │                                                         │
   │ Gunicorn WSGI Workers (4x)                              │
   │   └── Flask REST API Application                        │
   │                                                         │
   │ Systemd Service: helpdesk.service                       │
   │ Local Attachments: /var/www/helpdesk/backend/app/uploads│
   └────────────────────────┬────────────────────────────────┘
                            │ MySQL Port 3306 (Private Subnet)
                            ▼
           Amazon RDS MySQL or Private EC2 MySQL
```

---

## 2. Infrastructure & Cost Analysis (ap-southeast-2)

*Approximate on-demand pricing in USD; check official AWS Pricing Calculator before provisioning.*

| Resource | Specification | Purpose | Approx. Cost / Month |
|---|---|---|---|
| **EC2 Instance** | `t3.medium` (2 vCPU, 4 GiB RAM) | Nginx, Gunicorn, React build, Flask API | ~$30.00 / mo |
| **EBS Storage** | 30 GB gp3 SSD | OS, dependencies, local attachment uploads | ~$3.00 / mo |
| **Amazon RDS** | `db.t4g.micro` MySQL (Single-AZ) | Managed relational database | ~$18.00 / mo |
| *(Optional)* **Self-Hosted MySQL** | Run MySQL on second `t3.small` EC2 | Cost-effective isolated database | ~$15.00 / mo |
| **Elastic IP** | 1 IPv4 Allocated | Static ingress address | Free while attached to running instance |
| **SSL / HTTPS** | Let's Encrypt via Certbot | TLS 1.2 / 1.3 encryption | **Free** ($0.00) |

---

## 3. Security Group Rules (Strict Least-Privilege)

### Web / App Security Group (`helpdesk-app-sg`)
| Type | Protocol | Port Range | Source | Description |
|---|---|---|---|---|
| Inbound | TCP | 22 | `YOUR_OFFICE_IP/32` | SSH Administration (Never `0.0.0.0/0`) |
| Inbound | TCP | 80 | `0.0.0.0/0` | HTTP Ingress (Redirects to HTTPS) |
| Inbound | TCP | 443 | `0.0.0.0/0` | HTTPS Ingress (Encrypted traffic) |
| Outbound | All | All | `0.0.0.0/0` | Package updates, external AI API |

### Database Security Group (`helpdesk-db-sg`)
| Type | Protocol | Port Range | Source | Description |
|---|---|---|---|---|
| Inbound | TCP | 3306 | `sg-xxxx (helpdesk-app-sg)` | **MySQL access permitted ONLY from app server** |
| Outbound | All | None | None | Database locked down |

> [!WARNING]
> Never open port 3306 to `0.0.0.0/0`. The database must strictly reside in a private subnet or only accept packets from the application security group.

---

## 4. Step-by-Step EC2 Deployment Walkthrough

### Step 1: Launch EC2 Instance
1. Sign in to AWS Management Console and select region **ap-southeast-2 (Sydney)**.
2. Launch a new EC2 instance:
   - **AMI**: Ubuntu Server 22.04 LTS (HVM), SSD Volume Type.
   - **Instance Type**: `t3.medium`.
   - **Key Pair**: Select or create an Ed25519/RSA key pair.
   - **Security Group**: Attach `helpdesk-app-sg`.
   - **Storage**: 30 GiB gp3.

### Step 2: Provision Database
Either create an **Amazon RDS MySQL** instance (`db.t4g.micro`) or install MySQL Server on an internal server. Run:
```sql
SOURCE /path/to/database/create_db_and_user.sql;
SOURCE /path/to/database/schema.sql;
```

### Step 3: Run Deployment Provisioning
SSH into the EC2 instance and clone your repository:
```bash
ssh -i your-key.pem ubuntu@YOUR_EC2_PUBLIC_IP

sudo git clone https://github.com/your-username/AI-Customer-Support-Helpdesk.git /var/www/helpdesk
sudo chown -R ubuntu:ubuntu /var/www/helpdesk
```

Execute the automated provisioning script:
```bash
chmod +x /var/www/helpdesk/deployment/setup_ec2.sh
/var/www/helpdesk/deployment/setup_ec2.sh
```

### Step 4: Configure Production Secrets
Create `/var/www/helpdesk/backend/.env`:
```bash
cp /var/www/helpdesk/deployment/env.production.example /var/www/helpdesk/backend/.env
nano /var/www/helpdesk/backend/.env
```
Populate real values for `SECRET_KEY`, `DB_HOST`, `DB_PASSWORD`, and domain name.

### Step 5: Enable HTTPS Certificate
Run Certbot to automatically configure Let's Encrypt certificates:
```bash
sudo certbot --nginx -d helpdesk.yourdomain.com
```

### Step 6: Verify Live Services
```bash
sudo systemctl status helpdesk
sudo systemctl status nginx
curl -k https://127.0.0.1/api/v1/health
```
