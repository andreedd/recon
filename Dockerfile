# Use the official Nginx image as the base image
FROM nginx

# Copy your index.html file into the container's default document root directory
COPY index.html /usr/share/nginx/html/

# Expose port 80 (Nginx's default port)
EXPOSE 80

# Command to start Nginx in the foreground
CMD ["nginx", "-g", "daemon off;"]
