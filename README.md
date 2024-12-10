# Password Vault Project 🛡️

A secure password storage system using Dockerized microservices. This project handles user data, applies BCRYPT hashing, and ensures encryption via Google Tink.

---

## **Project Overview**

The project is divided into three components:
1. **Client**: A front-end interface for user interactions.
2. **Server1**: Manages user data (username/email, SALT, hashed password using BCRYPT).
3. **Server2**: Encrypts the BCRYPT hash using Google Tink.

---

## **Project Structure**

```
password_vault/
│
├── client/                     # Front-end client (user interface)
│   ├── static/images/          # Static resources (images)
│   ├── templates/              # HTML templates
│   ├── app.py                  # Client Flask server
│   ├── Dockerfile              # Docker configuration for client
│   └── requirements.txt        # Python dependencies for client
│
├── server1/                    # Microservice 1: User data + BCRYPT hashing
│   ├── app.py                  # Server 1 main logic
│   ├── Dockerfile              # Docker configuration for server1
│   └── requirements.txt        # Python dependencies for server1
│
├── server2/                    # Microservice 2: Google Tink encryption
│   ├── app.py                  # Server 2 main logic
│   ├── Dockerfile              # Docker configuration for server2
│   └── requirements.txt        # Python dependencies for server2
│
├── .gitignore                  # Ignored files for Git
├── docker-compose.yml          # Docker Compose file to orchestrate services
├── LICENSE                     # License file
└── README.md                   # Project documentation
```

---

## **Requirements**

- **Docker** installed and running
- **Docker Compose** (optional but recommended)

---

## **Setup Instructions**

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KyllianGenot/Password-Vault.git
   cd Password-Vault
   ```

2. **Build and run all services** using Docker Compose:
   ```bash
   docker-compose up --build
   ```

3. **Access the project**:
   - **Client**: Visit `http://localhost:5002` in your browser.
   - **Server1** and **Server2** run as backend services.

4. **Stop the containers**:
   ```bash
   docker-compose down
   ```

---

## **Notes**

- Ensure Docker is installed and properly configured.
- You can modify ports or environment variables in the `docker-compose.yml` file.
- Dependencies are managed using `requirements.txt` for each component.

---

## **License**

This project is licensed under the [MIT License](LICENSE).

---

By exploring this repository, you’ll gain hands-on experience with secure password storage, Dockerized microservices, and encryption techniques using BCRYPT and Google Tink. For further details, refer to the README.md in each project folder or open an issue on the repository.
