FROM node:16-bullseye-slim

ARG USERNAME=migrator
ARG USER_UID=2000
ARG USER_GID=$USER_UID

LABEL version="0.1.5"
LABEL description="Migrate Issues, Wiki from gitlab to github."

WORKDIR /app

# Add a non-root user, so later we can explore methods to scale
# privileges within this container.
# https://code.visualstudio.com/remote/advancedcontainers/add-nonroot-user#_creating-a-nonroot-user
RUN groupadd --gid $USER_GID $USERNAME
RUN useradd --uid $USER_UID --gid $USER_GID -m $USERNAME
RUN chown -R $USERNAME /app

# Copy the project contents to the container
COPY --chown=$USERNAME . /app

USER $USERNAME

# Install dependencies
RUN npm i

# Start the process
ENTRYPOINT ["/bin/bash", "-x", "/app/entrypoint.sh"]