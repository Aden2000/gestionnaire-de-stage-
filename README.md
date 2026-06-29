

# 📘 Gestionnaire de Stagiaire

Un système de gestion des stages développé avec **Django**, permettant aux entreprises et institutions de suivre les stagiaires, leurs projets, tâches, rapports hebdomadaires et finaux.

## 🚀 Fonctionnalités principales

- **Gestion des utilisateurs**  
  - Profils avec rôles : Ressource Humaine, Mentor, Stagiaire, Staff.  
  - Informations personnelles (département, téléphone, adresse).

- **Projets & Tâches**  
  - Création et suivi des projets attribués aux stagiaires.  
  - Gestion des tâches par semaine avec statut (non commencé, en cours, complété).  
  - Suivi de l’avancement (% de progression).

- **Documents & Rapports**  
  - Upload de documents liés aux projets.  
  - Rapports de stage (brouillon, soumis, examiné) avec validation par mentor.  
  - Rapports hebdomadaires avec suivi des activités, défis et prochaines étapes.  
  - Rapport final avec résumé, réalisations et recommandations.

- **Stages & Assignations**  
  - Création de stages avec département, description et exigences.  
  - Assignation des stagiaires aux stages avec suivi du statut (en attente, accepté, rejeté, complété).  

## 🛠️ Technologies utilisées

- **Backend** : Django (ORM, Models, Admin)  
- **Base de données** : PostgreSQL (ou SQLite en développement)  
- **Frontend** : Django Templates (HTML, CSS, JS)  
- **Stockage fichiers** : Django FileField (documents, rapports, captures d’écran)  

## 📂 Structure des modèles

- `UserProfile` : Profil utilisateur avec rôle et infos personnelles.  
- `Project` : Projet attribué à un stagiaire.  
- `Task` : Tâches hebdomadaires liées à un projet.  
- `Document` : Documents uploadés par stagiaires.  
- `InternshipReport` : Rapports de stage avec validation.  
- `Internship` : Stages disponibles.  
- `InternshipAssignment` : Assignations stagiaires ↔ stages.  
- `WeeklyReport` : Rapports hebdomadaires.  
- `FinalReport` : Rapport final de stage.  

## ⚙️ Installation et configuration

1. **Cloner le dépôt**  
   ```bash
   git clone https://github.com/Aden2000/gestionnaire-de-stage-.git
   cd gestionnaire-de-stage-
   ```

2. **Créer un environnement virtuel**  
   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. **Installer les dépendances**  
   ```bash
   pip install -r requirements.txt
   ```

4. **Appliquer les migrations**  
   ```bash
   python manage.py migrate
   ```

5. **Créer un superutilisateur**  
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancer le serveur**  
   ```bash
   python manage.py runserver
   ```

## 📊 Exemple d’utilisation

- Ressource Humaine crée un stage et assigne un stagiaire.  
- Le stagiaire reçoit un projet avec des tâches hebdomadaires.  
- Chaque semaine, il soumet un rapport hebdomadaire.  
- À la fin, il dépose un rapport final validé par le mentor.  

## 🤝 Contribution

Les contributions sont les bienvenues !  
- Forkez le projet  
- Créez une branche (`feature/ma-fonctionnalite`)  
- Faites un commit  
- Ouvrez une Pull Request  



---

👉 Aden, je peux aussi ajouter un **schéma visuel** (diagramme des relations entre modèles) pour rendre ton README encore plus attractif. Veux-tu que je génère un diagramme UML simplifié des modèles Django de ton projet ?
