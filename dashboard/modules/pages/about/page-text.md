## About the App 

This app visualises the results of habitat suitability modelling work carried out by South Yorkshire Bat Group. You can use the app to explore the predicted bat distribution across South Yorkshire.

**What is Habitat Suitability Modelling?** Habitat suitability modeling (also known as Species Distribution Modelling) is a technique used to predict the most favorable environments for particular species, such as bats, based on specific ecological and geographical criteria. This process starts by collecting and analysing data on locations where the species has been recorded and examining factors such as vegetation type, proximity to water sources, elevation, topography, and climate conditions. These data are then used to build a statistical model of the species' habitat preferences. The model extrapolates the preferences across a broader area, giving a detailed map of relative high and low predicted suitability. This mapping can be used as a guide for impact assessment and conservation planning, highlighting areas that support important habitat for the species.

**Data Sources and Methodology** 💾

The modelling used a Maximum Entropy model from the [`elapid`](https://earth-chris.github.io/elapid/) Python library. This implementation closely matches the popular [MaxEnt](https://biodiversityinformatics.amnh.org/open_source/maxent/) software package.

South Yorkshire Bat Group provided all bat records used in the modelling. Any records that did not have a grid refernce accuracy of 100m or less were removed from the modelling.

The modelling used the following data sources to define environmental variables as inputs to the model:
- WorldClim Climate Data
- EA LiDAR Data
- OS VectorMap District
- CEH Land Cover

**Project Contributors** ✉️

[**Greg Slack**](https://www.linkedin.com/in/greg-slack-9212064b/) *Principal Ecologist / Partner at Middleton Bell Ecology Ltd*

Greg is an accomplished ecologist who has managed ecological surveys, mitigation designs, and reporting for major infrastructure projects across the UK and Jordan, specialising in bat conservation and technical innovation. His work includes developing habitat suitability models and is the author of influential articles on bat survey data interpretation.


<br>

[**Matthew Whittle**](https://www.linkedin.com/in/matthewjwhittle/) *Associate Data Scientist, SLR Consulting*

Matt is an experienced data scientist with deep expertise in Ecology. He has led various elements of ecological assessment work as a consultant and developed habitat suitability models for multiple large ecological impact assessment projects. His work now focuses on the application of machine learning to solve challenges across various sustainability disciplines.
