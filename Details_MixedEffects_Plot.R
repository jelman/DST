library(nlme)
library(ggplot2)

infile <- "C:/Users/Jeremy/GradSchool/My Experiments/DST/results/Details/Details_Age_TaskNeg_long.csv"


DetailsData <- read.csv(infile)
DetailsData$Group <- factor(DetailsData$Group)
DetailsData$Detail.Level <- factor(DetailsData$Detail.Level)
contrasts(DetailsData$Detail.Level) <- contr.poly(5)

lmm <- lme(Z.score ~ Detail.Level*Group + GM + HitRate, data = DetailsData, random = ~ Detail.Level|Subject)
summary(lmm)

p <- ggplot(DetailsData, aes(x=Detail.Level, y=Z.score, colour=Group)) + 
geom_smooth(aes(group=Subject), method="lm", se=FALSE, size=.5, linetype="dashed") + 
geom_smooth(aes(group=Group), method="lm", se=FALSE, size=2) + theme_classic(24) + 
scale_color_manual(values = c("#377eb8", "#ff7f00")) + 
theme(legend.key = element_blank(),
axis.text.x = element_text(colour="black",size=18,face="plain"),
legend.title = element_blank(),
axis.text.y = element_text(colour="black",size=18,face="plain"),  
axis.title.x = element_text(colour="black",size=24,face="plain"),
axis.title.y = element_text(colour="black",size=24,face="plain")) + xlab("Detail Level") + ylab("Z score")

print(p)
