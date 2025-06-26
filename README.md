_Note: This is not the original repository. The project was copied over to preserve the original application while specifying and emphasizing personal contributions during the app's collaborative development._

# CIOnnect

Project management application for UVA students to connect to the many peer-led contracted independent organizations (CIOs) present all over Grounds.

This application was created in collaboration with Cassie Buxbaum, David Shtengel, Pratistha Dhungana, and Fares Habbab for CS 3240: Software Engineering _(Fall 2024)_.

Made using Django, Bootstrap, and Amazon S3 for cloud storage. The original project was hosted on Heroku.

## Overview

CIOnnect is a project management application (PMA) that allows users to create their own clubs and join other users' clubs. Within each club _"group"_/_"project,"_ users can add/delete files, create to-do lists, post messages, and more.

## Team Role – DevOps Manager

I acted as DevOps manager during the development of CIOnnect. My role-specific contributions included, but were not limited to, the following:
- Deployed the application to Heroku and configured Heroku’s PostgreSQL database, integrating it with the front-end.
  - _Note: The application is no longer hosted on Heroku._
- Set up cloud storage infrastructure using Amazon S3.
  - _(Note: For security purposes, the associated AWS access key has been deactivated and the account has been closed._
- Troubleshot and resolved infrastructure-related issues across deployment, database, and storage services.
- Assisted team members in debugging CI pipeline errors and infrastructure-related bugs, particularly with GitHub Actions.

My other general contributions included, but were not limited to, the following:
- Added Google login integration using OAuth
- Implemented features including to-do lists, file upload/deletion, and message posting
- Implemented group join and approval functionality
- Various front-end UI updates
