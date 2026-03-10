# syntax=docker/dockerfile:1.5

######## BUILD STAGE ########
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /workspace

# dependency cache trick
COPY app/pom.xml .

RUN mvn -B -q -e -DskipTests dependency:go-offline

# copy source
COPY app/src ./src

# build jar
RUN mvn -B -q -DskipTests package

######## RUNTIME STAGE ########
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app

RUN useradd -r -u 10001 appuser
USER 10001

COPY --from=build /workspace/target/*.jar /app/app.jar

EXPOSE 9001

ENTRYPOINT ["java","-jar","/app/app.jar"]