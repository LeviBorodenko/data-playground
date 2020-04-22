# Data Playground
_Fun and informal data analysis projects._


### 1. Destilling statistically significant circumstances that promote the lethality of a car accident.

We use a GLM approach to find covariates that have a high influence on the odds of lethality in a car accident. We use a dataset of roughly 250000 recorded car accidents in the UK.

[Methodology](/AccidentsUK/Analysis.pdf) and [data](https://data.gov.uk/dataset/cb7ae6f0-4be6-4935-9277-47e5ce24a11f/road-safety-data)

![Result](/AccidentsUK/chart.png)

### Simulating a Covid outbreak in Reddit

![Result](/Reddit-Outbreak/demo.png)

Simulating a Covid outbreak on Reddit using python. 

Every user commenting in a monitored thread gets his recent commenting history scanned and may infect users whose posts/comments tehy have commented. Once we have infected so many people in a subreddit that it is computationally not feasible to keep spreading on a case by case basis, a Covid SIR model takes over and simulates further spread in that subreddit.

We interact with reddit via PRAW and the fronend is build with vue.js and c3.js for the charts.