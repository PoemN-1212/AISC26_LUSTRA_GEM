"""
Từ điển ánh xạ từ khóa đồng nghĩa (Skill Aliases to Canonical Skill Mapping)
Dự án GEM (LUSTRA_GEM) - UIT AISC'26
Quy tắc: Nhóm mọi biến thể viết tắt, phiên bản, lỗi chính tả thường gặp về một CANONICAL SKILL duy nhất.
"""

from typing import Dict, Tuple

# Cấu trúc: alias.lower(): (canonical_name, category)
CANONICAL_ALIASES_MAP: Dict[str, Tuple[str, str]] = {
    # =========================================================================
    # 1. NGÔN NGỮ LẬP TRÌNH (PROGRAMMING LANGUAGES)
    # =========================================================================
    "python": ("Python", "PROGRAMMING_LANGUAGE"),
    "python3": ("Python", "PROGRAMMING_LANGUAGE"),
    "python 3": ("Python", "PROGRAMMING_LANGUAGE"),
    "javascript": ("JavaScript", "PROGRAMMING_LANGUAGE"),
    "js": ("JavaScript", "PROGRAMMING_LANGUAGE"),
    "ecmascript": ("JavaScript", "PROGRAMMING_LANGUAGE"),
    "typescript": ("TypeScript", "PROGRAMMING_LANGUAGE"),
    "ts": ("TypeScript", "PROGRAMMING_LANGUAGE"),
    "java": ("Java", "PROGRAMMING_LANGUAGE"),
    "java 8": ("Java", "PROGRAMMING_LANGUAGE"),
    "java 11": ("Java", "PROGRAMMING_LANGUAGE"),
    "java 17": ("Java", "PROGRAMMING_LANGUAGE"),
    "java core": ("Java", "PROGRAMMING_LANGUAGE"),
    "c#": ("C#", "PROGRAMMING_LANGUAGE"),
    "csharp": ("C#", "PROGRAMMING_LANGUAGE"),
    "c sharp": ("C#", "PROGRAMMING_LANGUAGE"),
    "c++": ("C++", "PROGRAMMING_LANGUAGE"),
    "cpp": ("C++", "PROGRAMMING_LANGUAGE"),
    "c": ("C", "PROGRAMMING_LANGUAGE"),
    "golang": ("Go", "PROGRAMMING_LANGUAGE"),
    "go": ("Go", "PROGRAMMING_LANGUAGE"),
    "php": ("PHP", "PROGRAMMING_LANGUAGE"),
    "php 7": ("PHP", "PROGRAMMING_LANGUAGE"),
    "php 8": ("PHP", "PROGRAMMING_LANGUAGE"),
    "ruby": ("Ruby", "PROGRAMMING_LANGUAGE"),
    "rust": ("Rust", "PROGRAMMING_LANGUAGE"),
    "kotlin": ("Kotlin", "PROGRAMMING_LANGUAGE"),
    "swift": ("Swift", "PROGRAMMING_LANGUAGE"),
    "dart": ("Dart", "PROGRAMMING_LANGUAGE"),
    "scala": ("Scala", "PROGRAMMING_LANGUAGE"),
    "r": ("R", "PROGRAMMING_LANGUAGE"),
    "sql": ("SQL", "PROGRAMMING_LANGUAGE"),
    "html": ("HTML", "PROGRAMMING_LANGUAGE"),
    "html5": ("HTML", "PROGRAMMING_LANGUAGE"),
    "css": ("CSS", "PROGRAMMING_LANGUAGE"),
    "css3": ("CSS", "PROGRAMMING_LANGUAGE"),

    # =========================================================================
    # 2. WEB FRONTEND & UI FRAMEWORKS
    # =========================================================================
    "react": ("React", "FRONTEND_FRAMEWORK"),
    "reactjs": ("React", "FRONTEND_FRAMEWORK"),
    "react.js": ("React", "FRONTEND_FRAMEWORK"),
    "react 18": ("React", "FRONTEND_FRAMEWORK"),
    "nextjs": ("Next.js", "FRONTEND_FRAMEWORK"),
    "next.js": ("Next.js", "FRONTEND_FRAMEWORK"),
    "next js": ("Next.js", "FRONTEND_FRAMEWORK"),
    "vue": ("Vue.js", "FRONTEND_FRAMEWORK"),
    "vuejs": ("Vue.js", "FRONTEND_FRAMEWORK"),
    "vue.js": ("Vue.js", "FRONTEND_FRAMEWORK"),
    "vue 3": ("Vue.js", "FRONTEND_FRAMEWORK"),
    "vuejs 3": ("Vue.js", "FRONTEND_FRAMEWORK"),
    "nuxtjs": ("Nuxt.js", "FRONTEND_FRAMEWORK"),
    "nuxt.js": ("Nuxt.js", "FRONTEND_FRAMEWORK"),
    "angular": ("Angular", "FRONTEND_FRAMEWORK"),
    "angularjs": ("Angular", "FRONTEND_FRAMEWORK"),
    "angular.js": ("Angular", "FRONTEND_FRAMEWORK"),
    "tailwind": ("TailwindCSS", "FRONTEND_FRAMEWORK"),
    "tailwindcss": ("TailwindCSS", "FRONTEND_FRAMEWORK"),
    "tailwind css": ("TailwindCSS", "FRONTEND_FRAMEWORK"),
    "bootstrap": ("Bootstrap", "FRONTEND_FRAMEWORK"),
    "bootstrap 5": ("Bootstrap", "FRONTEND_FRAMEWORK"),
    "sass": ("Sass", "FRONTEND_FRAMEWORK"),
    "scss": ("Sass", "FRONTEND_FRAMEWORK"),
    "redux": ("Redux", "FRONTEND_FRAMEWORK"),
    "redux toolkit": ("Redux", "FRONTEND_FRAMEWORK"),
    "rtk": ("Redux", "FRONTEND_FRAMEWORK"),

    # =========================================================================
    # 3. BACKEND & WEB SERVERS
    # =========================================================================
    "nodejs": ("Node.js", "BACKEND_FRAMEWORK"),
    "node.js": ("Node.js", "BACKEND_FRAMEWORK"),
    "node js": ("Node.js", "BACKEND_FRAMEWORK"),
    "node": ("Node.js", "BACKEND_FRAMEWORK"),
    "express": ("Express.js", "BACKEND_FRAMEWORK"),
    "expressjs": ("Express.js", "BACKEND_FRAMEWORK"),
    "express.js": ("Express.js", "BACKEND_FRAMEWORK"),
    "nestjs": ("NestJS", "BACKEND_FRAMEWORK"),
    "nest.js": ("NestJS", "BACKEND_FRAMEWORK"),
    "fastapi": ("FastAPI", "BACKEND_FRAMEWORK"),
    "fast api": ("FastAPI", "BACKEND_FRAMEWORK"),
    "django": ("Django", "BACKEND_FRAMEWORK"),
    "flask": ("Flask", "BACKEND_FRAMEWORK"),
    "spring": ("Spring Boot", "BACKEND_FRAMEWORK"),
    "spring boot": ("Spring Boot", "BACKEND_FRAMEWORK"),
    "springboot": ("Spring Boot", "BACKEND_FRAMEWORK"),
    "spring framework": ("Spring Boot", "BACKEND_FRAMEWORK"),
    "asp.net": ("ASP.NET Core", "BACKEND_FRAMEWORK"),
    "asp.net core": ("ASP.NET Core", "BACKEND_FRAMEWORK"),
    ".net": (".NET", "BACKEND_FRAMEWORK"),
    ".net core": (".NET", "BACKEND_FRAMEWORK"),
    "dotnet": (".NET", "BACKEND_FRAMEWORK"),
    "laravel": ("Laravel", "BACKEND_FRAMEWORK"),

    # =========================================================================
    # 4. MOBILE DEVELOPMENT
    # =========================================================================
    "flutter": ("Flutter", "MOBILE_FRAMEWORK"),
    "react native": ("React Native", "MOBILE_FRAMEWORK"),
    "react-native": ("React Native", "MOBILE_FRAMEWORK"),
    "android": ("Android", "MOBILE_FRAMEWORK"),
    "android sdk": ("Android", "MOBILE_FRAMEWORK"),
    "ios": ("iOS", "MOBILE_FRAMEWORK"),
    "ios sdk": ("iOS", "MOBILE_FRAMEWORK"),

    # =========================================================================
    # 5. CƠ SỞ DỮ LIỆU & STORAGE (DATABASES & CACHING)
    # =========================================================================
    "postgres": ("PostgreSQL", "DATABASE_STORAGE"),
    "postgresql": ("PostgreSQL", "DATABASE_STORAGE"),
    "pgsql": ("PostgreSQL", "DATABASE_STORAGE"),
    "mysql": ("MySQL", "DATABASE_STORAGE"),
    "mongodb": ("MongoDB", "DATABASE_STORAGE"),
    "mongo": ("MongoDB", "DATABASE_STORAGE"),
    "redis": ("Redis", "DATABASE_STORAGE"),
    "elasticsearch": ("Elasticsearch", "DATABASE_STORAGE"),
    "elastic search": ("Elasticsearch", "DATABASE_STORAGE"),
    "elastic": ("Elasticsearch", "DATABASE_STORAGE"),
    "sqlite": ("SQLite", "DATABASE_STORAGE"),
    "mssql": ("Microsoft SQL Server", "DATABASE_STORAGE"),
    "sql server": ("Microsoft SQL Server", "DATABASE_STORAGE"),
    "ms sql": ("Microsoft SQL Server", "DATABASE_STORAGE"),
    "oracle": ("Oracle Database", "DATABASE_STORAGE"),
    "oracle db": ("Oracle Database", "DATABASE_STORAGE"),
    "cassandra": ("Cassandra", "DATABASE_STORAGE"),
    "neo4j": ("Neo4j", "DATABASE_STORAGE"),
    "firebase": ("Firebase", "DATABASE_STORAGE"),
    "firestore": ("Firestore", "DATABASE_STORAGE"),

    # =========================================================================
    # 6. CLOUD & DEVOPS & INFRASTRUCTURE
    # =========================================================================
    "docker": ("Docker", "CLOUD_DEVOPS"),
    "docker compose": ("Docker", "CLOUD_DEVOPS"),
    "kubernetes": ("Kubernetes", "CLOUD_DEVOPS"),
    "k8s": ("Kubernetes", "CLOUD_DEVOPS"),
    "aws": ("AWS", "CLOUD_DEVOPS"),
    "amazon web services": ("AWS", "CLOUD_DEVOPS"),
    "gcp": ("Google Cloud Platform", "CLOUD_DEVOPS"),
    "google cloud": ("Google Cloud Platform", "CLOUD_DEVOPS"),
    "google cloud platform": ("Google Cloud Platform", "CLOUD_DEVOPS"),
    "azure": ("Microsoft Azure", "CLOUD_DEVOPS"),
    "microsoft azure": ("Microsoft Azure", "CLOUD_DEVOPS"),
    "git": ("Git", "CLOUD_DEVOPS"),
    "github": ("GitHub", "CLOUD_DEVOPS"),
    "gitlab": ("GitLab", "CLOUD_DEVOPS"),
    "ci/cd": ("CI/CD", "CLOUD_DEVOPS"),
    "cicd": ("CI/CD", "CLOUD_DEVOPS"),
    "ci": ("CI/CD", "CLOUD_DEVOPS"),
    "cd": ("CI/CD", "CLOUD_DEVOPS"),
    "jenkins": ("Jenkins", "CLOUD_DEVOPS"),
    "github actions": ("GitHub Actions", "CLOUD_DEVOPS"),
    "terraform": ("Terraform", "CLOUD_DEVOPS"),
    "ansible": ("Ansible", "CLOUD_DEVOPS"),
    "linux": ("Linux", "CLOUD_DEVOPS"),
    "ubuntu": ("Linux", "CLOUD_DEVOPS"),
    "nginx": ("Nginx", "CLOUD_DEVOPS"),

    # =========================================================================
    # 7. AI, MACHINE LEARNING & DATA SCIENCE
    # =========================================================================
    "machine learning": ("Machine Learning", "AI_DATA_SCIENCE"),
    "ml": ("Machine Learning", "AI_DATA_SCIENCE"),
    "deep learning": ("Deep Learning", "AI_DATA_SCIENCE"),
    "dl": ("Deep Learning", "AI_DATA_SCIENCE"),
    "artificial intelligence": ("Artificial Intelligence", "AI_DATA_SCIENCE"),
    "ai": ("Artificial Intelligence", "AI_DATA_SCIENCE"),
    "nlp": ("Natural Language Processing", "AI_DATA_SCIENCE"),
    "computer vision": ("Computer Vision", "AI_DATA_SCIENCE"),
    "cv": ("Computer Vision", "AI_DATA_SCIENCE"),
    "pytorch": ("PyTorch", "AI_DATA_SCIENCE"),
    "tensorflow": ("TensorFlow", "AI_DATA_SCIENCE"),
    "tf": ("TensorFlow", "AI_DATA_SCIENCE"),
    "keras": ("Keras", "AI_DATA_SCIENCE"),
    "scikit-learn": ("Scikit-Learn", "AI_DATA_SCIENCE"),
    "sklearn": ("Scikit-Learn", "AI_DATA_SCIENCE"),
    "pandas": ("Pandas", "AI_DATA_SCIENCE"),
    "numpy": ("NumPy", "AI_DATA_SCIENCE"),
    "opencv": ("OpenCV", "AI_DATA_SCIENCE"),
    "llm": ("Large Language Models", "AI_DATA_SCIENCE"),
    "large language model": ("Large Language Models", "AI_DATA_SCIENCE"),
    "rag": ("RAG", "AI_DATA_SCIENCE"),
    "huggingface": ("Hugging Face", "AI_DATA_SCIENCE"),
    "hugging face": ("Hugging Face", "AI_DATA_SCIENCE"),

    # =========================================================================
    # 8. API & KIẾN TRÚC HỆ THỐNG (API & ARCHITECTURE)
    # =========================================================================
    "rest api": ("REST API", "API_ARCHITECTURE"),
    "restful api": ("REST API", "API_ARCHITECTURE"),
    "restful apis": ("REST API", "API_ARCHITECTURE"),
    "restful": ("REST API", "API_ARCHITECTURE"),
    "rest": ("REST API", "API_ARCHITECTURE"),
    "graphql": ("GraphQL", "API_ARCHITECTURE"),
    "grpc": ("gRPC", "API_ARCHITECTURE"),
    "microservices": ("Microservices", "API_ARCHITECTURE"),
    "microservice": ("Microservices", "API_ARCHITECTURE"),
    "websocket": ("WebSocket", "API_ARCHITECTURE"),
    "kafka": ("Apache Kafka", "API_ARCHITECTURE"),
    "apache kafka": ("Apache Kafka", "API_ARCHITECTURE"),
    "rabbitmq": ("RabbitMQ", "API_ARCHITECTURE"),

    # =========================================================================
    # 9. TESTING & QA
    # =========================================================================
    "unit test": ("Unit Testing", "TESTING_QA"),
    "unit testing": ("Unit Testing", "TESTING_QA"),
    "automation test": ("Automated Testing", "TESTING_QA"),
    "automated testing": ("Automated Testing", "TESTING_QA"),
    "selenium": ("Selenium", "TESTING_QA"),
    "postman": ("Postman", "TESTING_QA"),
    "jmeter": ("JMeter", "TESTING_QA"),
    "jest": ("Jest", "TESTING_QA"),
    "cypress": ("Cypress", "TESTING_QA")
}
