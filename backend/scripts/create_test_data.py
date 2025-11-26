"""Create test data for the HITL service.

Run this script to populate the database with:
- Test user (reviewer)
- Test API key (for agent testing)
- Sample consultation requests

Usage:
    python -m scripts.create_test_data
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.session import SessionLocal
from app.models import User, APIKey, ConsultationRequest
from app.core.security import hash_password, generate_api_key, hash_api_key

def create_test_data():
    """Create test data."""
    db = SessionLocal()

    try:
        print("🚀 Creating test data...")

        # 1. Create test user
        print("\n1. Creating test user...")
        existing_user = db.query(User).filter(User.email == "reviewer@example.com").first()

        if existing_user:
            print("   ✓ Test user already exists")
            test_user = existing_user
        else:
            test_user = User(
                email="reviewer@example.com",
                name="Test Reviewer",
                hashed_password=hash_password("password123"),
                role="reviewer"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"   ✓ Created user: {test_user.email}")
            print(f"   📧 Email: reviewer@example.com")
            print(f"   🔑 Password: password123")

        # 2. Create test API key
        print("\n2. Creating test API key...")
        existing_key = db.query(APIKey).filter(APIKey.name == "test-agent").first()

        if existing_key:
            print("   ✓ Test API key already exists")
            print(f"   ⚠️  Cannot show the raw key (it was only shown once)")
        else:
            raw_key = generate_api_key()
            key_hash = hash_api_key(raw_key)

            test_api_key = APIKey(
                key_hash=key_hash,
                name="test-agent",
                description="Test API key for development"
            )
            db.add(test_api_key)
            db.commit()
            db.refresh(test_api_key)

            print(f"   ✓ Created API key: {test_api_key.name}")
            print(f"   🔑 RAW KEY (save this!): {raw_key}")
            print(f"   💾 You can use this key to test agent requests")

        # 3. Create sample consultation requests
        print("\n3. Creating sample consultation requests...")

        # Sample 1: Pending request
        sample1 = ConsultationRequest(
            title="Review High-Risk Database Schema Changes",
            description="Complaint #42 requires changes to the users table schema",
            context={
                "code_diff": """
@@ -10,6 +10,7 @@ CREATE TABLE users (
     email VARCHAR(255) UNIQUE NOT NULL,
     name VARCHAR(255),
+    phone VARCHAR(20),
     created_at TIMESTAMP DEFAULT NOW()
);
                """.strip(),
                "risk_level": "high",
                "affected_tables": ["users"],
                "estimated_impact": "5000 active users"
            },
            callback_webhook="https://httpbin.org/post",  # Test webhook
            state="pending",
            metadata={
                "workflow_id": "wf-test-001",
                "checkpoint_id": "cp-schema-review",
                "agent_id": "test-agent"
            }
        )
        db.add(sample1)

        # Sample 2: Another pending request
        sample2 = ConsultationRequest(
            title="Approve Deployment to Production",
            description="Code review passed, ready for production deployment",
            context={
                "commit_sha": "abc123def456",
                "branch": "feature/new-payment-flow",
                "tests_passed": True,
                "code_coverage": "94%"
            },
            callback_webhook="https://httpbin.org/post",
            state="pending",
            metadata={
                "workflow_id": "wf-test-002",
                "checkpoint_id": "cp-deploy-approval",
                "agent_id": "test-agent"
            }
        )
        db.add(sample2)

        db.commit()
        print(f"   ✓ Created 2 sample consultation requests")

        print("\n✅ Test data created successfully!")
        print("\n📖 Next steps:")
        print("   1. Start the backend: uvicorn app.main:app --reload")
        print("   2. Open Swagger UI: http://localhost:8000/docs")
        print("   3. Try logging in:")
        print("      - Email: reviewer@example.com")
        print("      - Password: password123")
        print("   4. Try the /auth/login endpoint to get a JWT token")
        print("   5. Use the token to access /requests endpoints")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    create_test_data()
