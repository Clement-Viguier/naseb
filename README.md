# NON AU SURF EN BOITE: Simulation de la demande en eau et en énergie

Ce code a pour objectif de quantifier précisément les besoins en eau et en énergie du projet de surf park à Canéjan porté par la société SCI Paola. Ce démarche est portée par certains membres du collectif "Canéjan en transition" opposé au projet, cependant, cette étude se veut rigoureuse et essaie d'établir une quantification précise et objective des besoins du projet. 

## Besoins en eau

TRAVAIL EN COURS

Le travail en cours consiste à modéliser la dynamiques des volumes d'eau dans les bassins et réservoirs dus aux précipitations et à l'évaporation. Ce travail se distingue du travail fait en amont de la demande de permis de construire par la société Ingetech et qui défend une autonomie en eau du projet par la prise en compte fine de la météo et évite d'utiliser des valeurs moyennes qui lissent les variation intra- et inter-annuelles.

Nous utilisons le package [`pywr`](https://github.com/pywr/pywr) pour modéliser les flux. Le package [`pyet`](https://pyet.readthedocs.io/en/latest/) est quand à lui utilisé pour modéliser l'évapotranspiration potentielle à partir de données météo mesurées.

Les modèles sont disponibles dans le dossier `models`, et les résultats de simulation sont dans le dossier `sims`.

Pour le moment le modèle de référence est le modèle `surf_park_no_city_water_split.json`. Les autres modèles considères les bassons comme un bassin unique, cela ne poserait pas de problème si le modèle implémentait une évaporation dynamique en fonction du volume d'eau (dépendant de quels bassins à de l'eau). Pour dépasser cette limite, les bassins sont séparés en séries et priorité est donnée au grand bassin comme signalé par les porteurs de projet.


## Besoin en énergie

NON COMMENCÉ

## En savoir plus sur le projet

Si cette analyse démontre que les besoins en eau et en énergie du projet dans sa forme initiale ne peuvent être remplis par les moyens de collecte mis en oeuvre, ce n'est qu'un des arguments de notre opposition à ce projet. L'autonomie en eau et énergie du projet, si elle était établie, ne suffirait pas à le rendre décent ou acceptable.

[Site internet](http://nonausurfenboite.fr/)

[Pétition](https://www.change.org/p/non-%C3%A0-la-m%C3%A9ga-piscine-%C3%A0-vagues-de-surf-%C3%A0-can%C3%A9jan-33-gironde)