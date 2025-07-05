# frontend/Dockerfile

# Use a specific version of Node.js for reproducibility
FROM node:20-alpine as build

ARG VITE_PUBLIC_API_BASE_URL
ENV VITE_PUBLIC_API_BASE_URL=${VITE_PUBLIC_API_BASE_URL}

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the SvelteKit app
RUN npm run build

# Use a smaller, more secure base image for the final image
FROM node:20-alpine

WORKDIR /app

# Copy build output from the build stage
COPY --from=build /app/build ./build
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json

# Expose the port the app will run on
EXPOSE 3000

# Command to run the app
CMD ["node", "build/index.js"]