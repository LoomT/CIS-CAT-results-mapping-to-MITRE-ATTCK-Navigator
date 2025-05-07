// src/translations.js
const translations = {
  en: {
    adminToken: 'Enter Admin Token',
    delete: 'Delete',
    visualize: 'Visualize',
    download: 'Download',
    uploadFile: 'Upload File',
    runBenchmark: 'Run Benchmark',
    filesList: 'Files List',
    userOverview: 'User Overview',
    adminOverview: 'Admin Overview',
    back: '← Back',
    cancel: 'Cancel',
    confirmDelete: name => `Are you sure you want to delete ${name}?`,
    chooseFormat: 'Choose a format to visualize'
  },
  nl: {
    adminToken: 'Voer admin token in',
    delete: 'Verwijder',
    visualize: 'Visualiseer',
    download: 'Downloaden',
    uploadFile: 'Bestand Uploaden',
    runBenchmark: 'Benchmark Uitvoeren',
    filesList: 'Bestandenlijst',
    userOverview: 'Gebruikersoverzicht',
    adminOverview: 'Beheeroverzicht',
    back: '← Terug',
    cancel: 'Annuleer',
    confirmDelete: name => `Weet je zeker dat je ${name} wilt verwijderen?`,
    chooseFormat: 'Kies een formaat om te visualiseren'
  }
};

export default translations;
