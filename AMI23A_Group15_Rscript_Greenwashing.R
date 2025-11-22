# Load necessary libraries
library(dplyr)
library(forcats)
library(ggplot2)

# Import the dataset
# path: C:/Users/hp/OneDrive - Högskolan Dalarna/Data Analysis and Visualisation/Project/Proj_files
dataset <- read.csv("C:/Users/hp/OneDrive - Högskolan Dalarna/Data Analysis and Visualisation/Project/Proj_files/output_final.csv")
# Including reports published after 2010
dataset <- subset(dataset, Year>2010)

###############################################################################################################################################

# Number of Reports from different sectors
ggplot(dataset, aes(factor(Sec_SASB))) + geom_bar(fill = "skyblue") +
  geom_text(stat = "count", aes(label = after_stat(count)), vjust = -0.5, colour = "black") +
  labs(title = "Number of Reports Analysed by Sector",
       x = "Sector",
       y = "Count") +
  theme_minimal() + theme(axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1))

# Number of Reports from different regions
ggplot(dataset, aes(factor(Region))) + geom_bar(fill = "lightgreen") +
  geom_text(stat = "count", aes(label = after_stat(count)), vjust = -0.5, colour  ="black") +
  labs(title = "Number of Reports Analysed by Region",
       x = "Region",
       y = "Count") +
  theme_minimal()

# Number of Reports from different companies by size
ggplot(dataset, aes(factor(Size))) + geom_bar(fill = "lavender") +
  geom_text(stat = "count", aes(label = after_stat(count)), vjust = -0.5, colour  ="black") +
  labs(title = "Number of Reports Analysed by Company Size",
       x = "Region",
       y = "Count") +
  theme_minimal()

###############################################################################################################################################

# Group by sector aggregating over time and count total reports and greenwashed reports based on greenwashed score
sectorSASB_over_time <- dataset %>%
  group_by(Sec_SASB) %>%
  summarise(
    total_reports = n(),  # Total number of reports per sector
    greenwashing = sum(Greenwashing_Result == 'Greenwashing')  # Number of Greenwashed reports
  ) %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

# Displaying greenwashing in specific sectors over the years
ggplot(sectorSASB_over_time, aes(fct_reorder(Sec_SASB, greenwashed_pcnt), 
                                 greenwashed_pcnt, fill = Sec_SASB)) + geom_bar(stat = "identity") + 
  coord_flip() + labs(title = "Total Greenwashing by Sector",
                      x = "Sector",
                      y = "Greenwashed Percentage") +
  theme_minimal() +
  theme(legend.position = "none")

###############################################################################################################################################

# Group by region aggregating over time and count total reports and greenwashed reports based on greenwashed score
region_over_time <- dataset %>%
  group_by(Region) %>%
  summarise(
    total_reports = n(),  # Total number of reports by Region
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

# Displaying greenwashing in specific sectors over the years
ggplot(region_over_time, aes(fct_reorder(Region, greenwashed_pcnt), 
                             greenwashed_pcnt, fill = Region)) + geom_bar(stat = "identity") + 
  coord_flip() + labs(title = "Total Greenwashing by Region",
                      x = "Region",
                      y = "Greenwashed Percentage") +
  theme_minimal() +
  theme(legend.position = "none")

###############################################################################################################################################

# Group by Company Size aggregating over time and count total reports and greenwashed reports based on greenwashed score
CompSize_over_time <- dataset %>%
  group_by(Size) %>%
  summarise(
    total_reports = n(),  # Total number of reports by Region
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

# Displaying greenwashing in specific sectors over the years
ggplot(CompSize_over_time, aes(fct_reorder(Size, greenwashed_pcnt), 
                             greenwashed_pcnt, fill = Size)) + geom_bar(stat = "identity") + 
  coord_flip() + labs(title = "Total Greenwashing by Company SIze",
                      x = "Company Size",
                      y = "Greenwashed Percentage") +
  theme_minimal() +
  theme(legend.position = "none")

###############################################################################################################################################

par(mfrow = c(5,3))
# Group by sector (Sec_SASB variable) and year and count total reports and greenwashed reports based on greenwashed score
secSASB_year_summary <- dataset %>%
  group_by(Year, Sec_SASB) %>%
  summarise(
    total_reports = n(),  # Total number of reports per Sector per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(secSASB_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() + facet_wrap(~Sec_SASB) +
labs(title = "Greenwashing by Sector by Year",
     x = "Year",
     y = "Greenwashed Percentage") +
  theme_minimal()

###############################################################################################################################################

# Group by region and year and count total reports and greenwashed reports based on greenwashed score
region_year_summary <- dataset %>%
  group_by(Year, Region) %>%
  summarise(
    total_reports = n(),  # Total number of reports per Region per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(region_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() +
  geom_line() + facet_wrap(~Region) +
labs(title = "Greenwashing by Region by Year",
     x = "Year",
     y = "Greenwashed Percentage") +
  theme_minimal()

###############################################################################################################################################

# Group by company size and year and count total reports and greenwashed reports based on greenwashed score
companysize_year_summary <- dataset %>%
  group_by(Year, Size) %>%
  summarise(
    total_reports = n(),  # Total number of reports per Company Size per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(companysize_year_summary, aes(Year, greenwashed_pcnt)) + 
  geom_point() + geom_line() + facet_wrap(~Size) +
labs(title = "Greenwashing by Size of the Company by Year",
     x = "Year",
     y = "Greenwashed Percentage") +
  theme_minimal()

###############################################################################################################################################

# Group by Sector(Sector variable) year and count total reports and greenwashed reports based on greenwashed score
sector_year_summary <- dataset %>%
  group_by(Year, Sector) %>%
  summarise(
    total_reports = n(),  # Total number of reports per Sector per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(sector_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() + facet_wrap(~Sector) +
  labs(title = "Greenwashing by Sector by Year",
       x = "Year",
       y = "Greenwashed Percentage") +
  theme_minimal()

###############################################################################################################################################

# For a few sectors
# Group year and count total reports and greenwashed reports

# Agriculture
Agri_year_summary <- dataset %>%
  filter(Sector == 'Agriculture') %>% 
  group_by(Year) %>%
  summarise(
    total_reports = n(),  # Total number of reports per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(Agri_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() +   labs(title = "Greenwashing by Year (Agriculture)",
                       x = "Year",
                       y = "Greenwashed Percentage") +
  theme_minimal()

# Food and Beverages
Food_year_summary <- dataset %>%
  filter(Sector == 'Food and Beverage Products') %>% 
  group_by(Year) %>%
  summarise(
    total_reports = n(),  # Total number of reports per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(Food_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() +   labs(title = "Greenwashing by Year (Food and Beverage Products)",
                       x = "Year",
                       y = "Greenwashed Percentage") +
  theme_minimal()

# Household and Personal Products
HPP_year_summary <- dataset %>%
  filter(Sector == 'Household and Personal Products') %>% 
  group_by(Year) %>%
  summarise(
    total_reports = n(),  # Total number of reports per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(HPP_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() +   labs(title = "Greenwashing by Year (Household and Personal Products)",
                       x = "Year",
                       y = "Greenwashed Percentage") +
  theme_minimal()

# Textiles and Apparel
Textile_year_summary <- dataset %>%
  filter(Sector == 'Textiles and Apparel') %>% 
  group_by(Year) %>%
  summarise(
    total_reports = n(),  # Total number of reports per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(Textile_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() +   labs(title = "Greenwashing by Year (Textiles and Apparel)",
                       x = "Year",
                       y = "Greenwashed Percentage") +
  theme_minimal()

# Computers
Computer_year_summary <- dataset %>%
  filter(Sector == 'Computers') %>% 
  group_by(Year) %>%
  summarise(
    total_reports = n(),  # Total number of reports per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(Computer_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() +   labs(title = "Greenwashing by Year (Computers)",
                       x = "Year",
                       y = "Greenwashed Percentage") +
  theme_minimal()

# For some countries/ region
# Brazil
Brazil_year_summary <- dataset %>%
  filter(Sector == 'Brazil') %>% 
  group_by(Year) %>%
  summarise(
    total_reports = n(),  # Total number of reports per year
    greenwashing = sum(Greenwashing_Result == 'Greenwashing') # Number of Greenwashed reports
  )  %>%
  mutate(# Calculate greenwashed percentage
    greenwashed_pcnt = (greenwashing/ total_reports) * 100)

ggplot(Brazil_year_summary, aes(Year, greenwashed_pcnt)) + geom_point() + 
  geom_line() +   labs(title = "Greenwashing by Year (Brazil)",
                       x = "Year",
                       y = "Greenwashed Percentage") +
  theme_minimal()
###############################################################################################################################################

