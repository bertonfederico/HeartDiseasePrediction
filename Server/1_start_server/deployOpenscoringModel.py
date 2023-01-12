from openscoring import Openscoring


############################################
####### exporting pmml pipeline model ######
############################################
os = Openscoring("http://localhost:8080/openscoring")

# Shall be available at http://localhost:8080/openscoring/model/HeartDisease
os.deployFile("HeartDisease", "../outputModel/HeartDisease.pmml")