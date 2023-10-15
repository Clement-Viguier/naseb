
library(tidyverse)
library(ggplot2)
library(wesanderson)
library(RColorBrewer)


weather <- read.csv('/home/clement_recovery/code/naseb/data/weather_data.csv')

volume_bassin2 = 13000
volume_bassin1 = 7000
total_volume <- volume_bassin1+volume_bassin2

capacities <- c(0, volume_bassin2, total_volume)
tolerance <- 0.05

folder_path <- "/home/clement_recovery/code/naseb/sim"

file_list <- list.files(folder_path)

# Loop over each file in the list
for (file_name in file_list) {
  tryCatch({
    print(file_name)
    sim_no_water <- read.csv(paste0(folder_path, '/', file_name))
    
    
    sim_no_water <- sim_no_water %>% mutate(capacity = case_when(
      bassin_volume < volume_bassin2*(1-tolerance) ~ 0,
      # bassin_volume < volume_bassin2*(1-tolerance) ~ volume_bassin1,
      bassin_volume < total_volume*(1-tolerance) ~ volume_bassin2, 
      .default = total_volume)
    )
    
    weekly_no_water <- sim_no_water %>%
      filter(year>1992) %>% 
      group_by(year, weekofyear) %>% 
      summarise(
        rain_water_flow = sum(rainwater_flow),
        pet_flow = sum(pet_flow),
        rainwater_flow = sum(rainwater_flow),
        bassin_rainwater_flow = sum(bassin_rainwater_flow),
        capacity = median(capacity),
        bassin_volume = mean(bassin_volume)
      )
    
    
    pal <- rev(wes_palette("Zissou1", 100, type = "continuous"))
    # pal <- brewer.pal(n = 8, name = "RdBu")
    n <-  6
    
    p1 <- ggplot(weekly_no_water, aes(x = weekofyear, y = year, color = bassin_volume))+
      scale_y_continuous(breaks = c(1992, 2002, 2012, 2022))
    brk <- ggplot_build(p1)$layout$panel_params[[1]]$y$breaks
    
    vplot <- weekly_no_water %>%
      ggplot() +
      geom_tile(aes(x=weekofyear, y=year, fill=(bassin_volume/(total_volume)*100)), colour="white", size=0.2)+
      scale_fill_gradientn(colours = pal, breaks = seq(0,100, length.out = n),
                           labels = seq(0,100, length.out = n) %>% round(2))+
      coord_polar()+
      theme_minimal()+
      scale_y_continuous(limits = c(1980, 2023))+
      labs(fill="Taux de remplissage", y='', x='')+
      annotate('text', x = 0, y = brk, label = as.character(brk), hjust=1, size=2)+
      scale_x_continuous(breaks = seq(1, 52, length.out = 12), labels = month.abb, limits = c(0, 58))+
      theme(axis.ticks.y=element_blank(),
            axis.text.y=element_blank(),
            panel.grid = element_blank(),
            axis.ticks.x=element_blank(),
      )
    
    
    output_file <- paste0("/home/clement_recovery/code/naseb/sim/plots/", file_name, "_volume_plot.png")
    ggsave(output_file, plot = vplot, width = 8, height = 6) 
    
    cols <- rev(wes_palette(n=5, name="Zissou1"))[c(1, 2, 5)]
    labs <- c("Aucun bassin", "Grand bassin", "Deux bassins")
    weekly_no_water$capacity_f <- factor(weekly_no_water$capacity, labels = labs, levels = capacities)
    cplot <- weekly_no_water %>%
      ggplot() +
      geom_tile(aes(x=weekofyear, y=year, fill=capacity_f), colour="white", size=0.2)+
      scale_fill_manual(values=cols)+
      coord_polar()+
      theme_minimal()+
      scale_y_continuous(limits = c(1980, 2023))+
      labs(fill="Capacité", y='', x='')+
      annotate('text', x = 0, y = brk, label = as.character(brk), hjust=1, size=2)+
      scale_x_continuous(breaks = seq(1, 52, length.out = 12), labels = month.abb, limits = c(0, 58))+
      theme(axis.ticks.y=element_blank(),
            axis.text.y=element_blank(),
            panel.grid = element_blank(),
            axis.ticks.x=element_blank(),
      )
    
    output_file <- paste0("/home/clement_recovery/code/naseb/sim/plots/", file_name, "_capacity_plot.png")
    ggsave(output_file, plot = cplot, width = 8, height = 6) 
  }, error = function(e) {
    cat("An error occurred: ", conditionMessage(e), "\n")
    -1  # You can return a value or perform other error handling here
  })
  
}