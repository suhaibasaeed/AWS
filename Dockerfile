# Base image that docker image uses
FROM centos:latest
LABEL maintainer="Animals4life"
# Creates new fs layer - installing the apache webserver
RUN yum -y install httpd
# Copy files from current dir into docker image - Each statement creates new fs layer
COPY index.html /var/www/html/
COPY containerandcat*.jpg /var/www/html/
# Set application which is being run - apache web serber in our case
ENTRYPOINT ["/usr/sbin/httpd", "-D", "FOREGROUND"]
# Expose port 80 of container so we can access web server
EXPOSE 80
