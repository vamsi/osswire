from database import engine, Base
from models import User, Post, Comment, LicenseType, CategoryType, LanguageType, SubmissionType
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

# Create tables
Base.metadata.create_all(bind=engine)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Create users
users = []
for i in range(1, 6):
    user = User(
        id=f"user_{i}",
        username=f"user{i}",
        email=f"user{i}@example.com",
        password_hash="hashed_password_here"
    )
    users.append(user)
    db.add(user)

# Real open source projects from GitHub and GitLab
posts_data = [
    {
        "title": "React - A JavaScript library for building user interfaces",
        "url": "https://github.com/facebook/react",
        "content": "React is a JavaScript library for building user interfaces. It is maintained by Facebook and a community of individual developers and companies.",
        "license": LicenseType.MIT,
        "category": CategoryType.WEB_FRAMEWORK,
        "language": LanguageType.JAVASCRIPT,
        "submission_type": SubmissionType.LIBRARY,
        "points": 156
    },
    {
        "title": "Vue.js - The Progressive JavaScript Framework",
        "url": "https://github.com/vuejs/vue",
        "content": "Vue.js is a progressive, incrementally-adoptable JavaScript framework for building UI on the web.",
        "license": LicenseType.MIT,
        "category": CategoryType.WEB_FRAMEWORK,
        "language": LanguageType.JAVASCRIPT,
        "submission_type": SubmissionType.FRAMEWORK,
        "points": 234
    },
    {
        "title": "FastAPI - Modern, fast web framework for building APIs",
        "url": "https://github.com/tiangolo/fastapi",
        "content": "FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.",
        "license": LicenseType.MIT,
        "category": CategoryType.WEB_FRAMEWORK,
        "language": LanguageType.PYTHON,
        "submission_type": SubmissionType.FRAMEWORK,
        "points": 201
    },
    {
        "title": "Rust - Empowering everyone to build reliable and efficient software",
        "url": "https://github.com/rust-lang/rust",
        "content": "Rust is a systems programming language that runs blazingly fast, prevents segfaults, and guarantees thread safety.",
        "license": LicenseType.MIT,
        "category": CategoryType.PROGRAMMING_LANGUAGE,
        "language": LanguageType.RUST,
        "submission_type": SubmissionType.SHOW,
        "points": 189
    },
    {
        "title": "Django - The Web framework for perfectionists with deadlines",
        "url": "https://github.com/django/django",
        "content": "Django is a high-level Python Web framework that encourages rapid development and clean, pragmatic design.",
        "license": LicenseType.BSD_3,
        "points": 167
    },
    {
        "title": "Node.js - JavaScript runtime built on Chrome's V8 JavaScript engine",
        "url": "https://github.com/nodejs/node",
        "content": "Node.js is a JavaScript runtime built on Chrome's V8 JavaScript engine. Node.js uses an event-driven, non-blocking I/O model.",
        "license": LicenseType.MIT,
        "points": 178
    },
    {
        "title": "PostgreSQL - The world's most advanced open source relational database",
        "url": "https://github.com/postgres/postgres",
        "content": "PostgreSQL is a powerful, open source object-relational database system with over 30 years of active development.",
        "license": LicenseType.BSD_3,
        "points": 145
    },
    {
        "title": "GitLab - The DevOps platform",
        "url": "https://gitlab.com/gitlab-org/gitlab",
        "content": "GitLab is a complete DevOps platform that enables professionals to perform all the tasks in a project—from project planning and source code management to monitoring and security.",
        "license": LicenseType.MIT,
        "points": 123
    },
    {
        "title": "TensorFlow - An Open Source Machine Learning Framework",
        "url": "https://github.com/tensorflow/tensorflow",
        "content": "TensorFlow is an open source software library for numerical computation using data flow graphs.",
        "license": LicenseType.APACHE_2_0,
        "points": 212
    },
    {
        "title": "Kubernetes - Production-Grade Container Orchestration",
        "url": "https://github.com/kubernetes/kubernetes",
        "content": "Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications.",
        "license": LicenseType.APACHE_2_0,
        "points": 198
    },
    {
        "title": "Docker - Empowering App Development for Developers",
        "url": "https://github.com/docker/docker-ce",
        "content": "Docker is an open platform for developing, shipping, and running applications. Docker enables you to separate your applications from your infrastructure.",
        "license": LicenseType.APACHE_2_0,
        "points": 176
    },
    {
        "title": "Redis - In-Memory Data Structure Store",
        "url": "https://github.com/redis/redis",
        "content": "Redis is an open source, in-memory data structure store, used as a database, cache, message broker, and queue.",
        "license": LicenseType.BSD_3,
        "points": 134
    },
    {
        "title": "Elasticsearch - Search and Analytics Engine",
        "url": "https://github.com/elastic/elasticsearch",
        "content": "Elasticsearch is a distributed, RESTful search and analytics engine capable of solving a growing number of use cases.",
        "license": LicenseType.APACHE_2_0,
        "points": 156
    },
    {
        "title": "MongoDB - The database for modern applications",
        "url": "https://github.com/mongodb/mongo",
        "content": "MongoDB is a source-available cross-platform document-oriented database program. Classified as a NoSQL database program.",
        "license": LicenseType.APACHE_2_0,
        "points": 143
    },
    {
        "title": "GraphQL - A query language for APIs",
        "url": "https://github.com/graphql/graphql-js",
        "content": "GraphQL is a query language for APIs and a runtime for fulfilling those queries with your existing data.",
        "license": LicenseType.MIT,
        "points": 167
    },
    {
        "title": "TypeScript - Typed JavaScript at Any Scale",
        "url": "https://github.com/microsoft/TypeScript",
        "content": "TypeScript is a strongly typed programming language that builds on JavaScript, giving you better tooling at any scale.",
        "license": LicenseType.APACHE_2_0,
        "points": 189
    },
    {
        "title": "Next.js - The React Framework for Production",
        "url": "https://github.com/vercel/next.js",
        "content": "Next.js gives you the best developer experience with all the features you need for production: hybrid static & server rendering.",
        "license": LicenseType.MIT,
        "points": 201
    },
    {
        "title": "Tailwind CSS - A utility-first CSS framework",
        "url": "https://github.com/tailwindlabs/tailwindcss",
        "content": "Tailwind CSS is a utility-first CSS framework for rapidly building custom user interfaces.",
        "license": LicenseType.MIT,
        "points": 178
    },
    {
        "title": "Laravel - The PHP Framework for Web Artisans",
        "url": "https://github.com/laravel/laravel",
        "content": "Laravel is a web application framework with expressive, elegant syntax. We believe development must be an enjoyable experience.",
        "license": LicenseType.MIT,
        "points": 145
    },
    {
        "title": "Spring Boot - Java-based framework for building web applications",
        "url": "https://github.com/spring-projects/spring-boot",
        "content": "Spring Boot makes it easy to create stand-alone, production-grade Spring based Applications that you can 'just run'.",
        "license": LicenseType.APACHE_2_0,
        "points": 167
    },
    {
        "title": "Flutter - Google's UI toolkit for building beautiful apps",
        "url": "https://github.com/flutter/flutter",
        "content": "Flutter is Google's UI toolkit for building beautiful, natively compiled applications for mobile, web, and desktop from a single codebase.",
        "license": LicenseType.BSD_3,
        "points": 198
    },
    {
        "title": "Angular - Platform for building mobile and desktop web applications",
        "url": "https://github.com/angular/angular",
        "content": "Angular is a platform for building mobile and desktop web applications using TypeScript/JavaScript and other languages.",
        "license": LicenseType.MIT,
        "points": 187
    }
]

# Create posts
posts = []
for i, post_data in enumerate(posts_data):
    # Randomly assign users to posts
    user = random.choice(users)
    
    # Create post with timestamp
    post = Post(
        id=f"post_{i+1}",
        title=post_data["title"],
        url=post_data["url"],
        content=post_data["content"],
        license=post_data["license"],
        category=post_data.get("category"),
        language=post_data.get("language"),
        submission_type=post_data.get("submission_type"),
        created_by=user.id,
        points=post_data["points"],
        created_at=datetime.now() - timedelta(days=random.randint(0, 30))
    )
    posts.append(post)
    db.add(post)

# Create some comments
comments_data = [
    "This is exactly what I needed for my project!",
    "Great find, thanks for sharing!",
    "I've been using this for months, highly recommend.",
    "This looks promising, will give it a try.",
    "Excellent documentation and community support.",
    "Perfect timing, I was just looking for something like this.",
    "The performance is incredible!",
    "Love the simplicity and ease of use.",
    "This has saved me so much time.",
    "Highly recommend for anyone working with similar tech.",
    "The API is very well designed.",
    "Great alternative to the existing solutions.",
    "This is becoming my go-to tool.",
    "The learning curve is surprisingly gentle.",
    "Excellent choice for production use.",
    "This project has a bright future ahead.",
    "The community is very helpful and active.",
    "I'm impressed with the code quality.",
    "This solves a real problem I was facing.",
    "The documentation is comprehensive and clear."
]

# Create comments for posts
for post in posts:
    # Add 1-3 comments per post
    num_comments = random.randint(1, 3)
    for _ in range(num_comments):
        user = random.choice(users)
        comment = Comment(
            id=f"comment_{len(comments_data)}_{random.randint(1000, 9999)}",
            content=random.choice(comments_data),
            created_by=user.id,
            submission_id=post.id,
            created_at=datetime.now() - timedelta(days=random.randint(0, 7))
        )
        db.add(comment)

# Commit all changes
db.commit()
db.close()

print("Database seeded successfully!")
print(f"Created {len(users)} users")
print(f"Created {len(posts)} posts")
print(f"Created {len(comments_data)} comments")

