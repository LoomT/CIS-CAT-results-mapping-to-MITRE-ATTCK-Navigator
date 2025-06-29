const translations = {
  en: {
    // tab names
    titleMapper: 'CIS-CAT Results Mapper to MITTRE ATT\&CK Navigator',
    titleFileUpload: 'Manual File Upload',
    titleReports: 'View Reports',
    titleUserDepartmentManagement: 'Users and Departments Management',
    titleBearerTokenManagement: 'Token Management',

    // misc
    loading: 'Loading...',
    from: 'From',
    to: 'To',
    searching: 'Searching',
    search: 'Search',
    export: 'Export',
    visualize: 'Visualize',
    download: 'Download',
    select: 'Select',
    cancel: 'Cancel',
    noOptions: 'No options',
    actions: 'Actions',
    department: 'Department',
    createdAt: 'Created at',
    lastUsed: 'Last Used',
    createdBy: 'Created By',
    important: 'Important',
    machine: 'Machine',
    copy: 'Copy',
    close: 'Close',
    delete: 'Delete',
    remove: 'Remove',
    name: 'Name',
    date: 'Date',
    create: 'Create',

    // Labels for landing screen
    homePickScreen: 'Pick a screen',
    homeViewReports: 'View Reports',
    homeBearerTokenManagement: 'Bearer Token Management',
    homeUserDepartmentManagement: 'Users and Departments Management',
    homeFileUpload: 'Manual File Upload',

    // roles
    roleSuperAdmin: 'Super Admin',
    roleDepartmentAdmin: 'Department Admin',
    roleUser: 'User',
    roleGuestUser: 'Guest User',

    // Reports overview
    reportsOverview: 'Reports overview',
    filterFiles: 'Filter files',
    searchByFilename: 'Filter by filename',
    searchFilenameText: 'Search files...',
    searchByDepartment: 'Filter by department',
    searchByHost: 'Filter by host',
    searchByDateRange: 'Search within date range',
    searchByBenchmark: 'Filter by Benchmark',
    showNFiles: n => (n !== 1 ? `Showing ${n} files` : `Showing ${n} file`),
    exportInProgress: 'Export in Progress',

    aggregation: 'Aggregation',
    noFilesSelected: 'No Files Selected',
    selectedFiles: 'Selected Files',
    noMoreFilesToLoad: 'No more files to load',
    exportChooseAFormatToVisualize: 'Choose a format to visualize',
    exportAgrregatePDF: 'Aggregate PDF',
    exportAllPDF: 'All PDF',

    // Manual file upload
    uploadDepartmentRequired: 'Please select a department before uploading',
    uploadInvalidFileType: 'Please upload a JSON file',
    uploadLimitExceeded: 'You can only upload one file at a time. Please try again.',
    uploadFile: 'Upload File',
    dragAndDrop: 'Drag and drop a file or click the area below to upload your JSON file.',
    dragAndDropShort: 'Drag and drop files here',
    orr: 'or',
    chooseFile: 'Choose file',
    selectDepartment: 'Select Department',
    selectDepartmentPlaceholder: 'Select a department',
    selectNoDepartment: 'Please select a department',
    failedToLoadDepartments: 'Failed to load departments',

    // Token Management
    tokenFailedFetch: 'Failed to fetch bearer tokens',
    errorFetchingTokens: 'Error fetching bearer tokens',
    machineNameEmpty: 'Machine name cannot be empty',
    tokenCreatedSuccessfully: 'Bearer token created successfully',
    tokenFailedToCreate: 'Failed to create bearer token',
    errorCreatingToken: 'Error creating bearer token',
    tokenRevokeConfirmation: 'Are you sure you want to revoke this token? This action cannot be undone.',
    tokenRevokedSuccessfully: 'Token revoked successfully',
    failedToRevokeToken: 'Failed to revoke token',
    errorRevokingToken: 'Error revoking token',
    tokenCopied: 'Token copied to clipboard',
    tokenNotCopied: 'Failed to copy token',

    createNewToken: 'Create New Token',
    machineName: 'Machine name',
    machineNamePlaceholder: 'e.g., Production Server 1',
    generateToken: 'Generate Token',
    usageInstructions: 'Usage Instructions',
    usageInstructionsP1: 'Bearer tokens allow automated systems to upload assessment results.',
    usageInstructionsP2: 'Configure your .wrapper.env file with:',
    fakeURL: 'your-domain.com',
    fakeToken: 'your-token-here',
    activeTokens: 'Active Bearer Tokens',
    noActiveTokensForDepartment: 'No active tokens for the selected department.',
    revoke: 'Revoke',

    tokenCreated: 'Bearer Token Created',
    displayMsg: 'This token will only be shown once. Please copy it now.',

    // User management Dashboard
    depFailedFetch: 'Failed to fetch departments',
    errorFetchingDep: 'Error fetching departments',
    usersFailedFetch: 'Failed to fetch users',
    errorFetchingUsers: 'Error fetching users',
    depNameCannotBeEmpty: 'Department name cannot be empty',
    depCreatedSuccessfully: 'Department created successfully',
    depFailedCreate: 'Failed to create department',
    errorCreatingDep: 'Error creating department',
    userHandleEmpty: 'User handle cannot be empty',
    userAddedToDepSuccess: 'User added to department successfully',
    userFailedAddToDep: 'Failed to add user to department',
    errorAddUserToDep: 'Error adding user to department',
    userRemovedSuccess: 'User removed from department successfully',
    userFailedRemoveFromDep: 'Failed to remove user from department',
    errorRemovingUserFromDep: 'Error removing user from department',
    depRemovalConfirmation: 'Are you sure you want to delete this department? This will remove all user assignments.',
    depDeletedSuccess: 'Department deleted successfully',
    depFailedDelete: 'Failed to delete department',
    errorDeletingDep: 'Error deleting department',
    userDepartmentDashboard: 'Users and Departments Management Dashboard',
    departmentManagement: 'Department Management',
    createNewDep: 'Create New Department',
    createDepPlaceholder: 'Department name',
    addUserToDep: 'Add User to Department',
    userHandle: 'User handle',
    addUser: 'Add User',
    currentDepAssignments: 'Current Department Assignments',
    noDepMessage: 'No departments created yet. Create your first department using the form above.',
    deleteDep: 'Delete Department',
    noUsersAtDep: 'No users assigned to this department',
    removeUserFromDep: 'Remove user from department',
    usersAssigned: num => (num !== 1 ? `${num} users assigned` : `${num} user assigned`),
    assigned: 'assigned',
  },
  nl: {
    // tab names
    titleMapper: 'CIS-CAT-Resultaten naar MITRE ATT&CK Navigator',
    titleFileUpload: 'Handmatig bestand uploaden',
    titleReports: 'Rapporten bekijken',
    titleUserDepartmentManagement: 'Gebruikers en afdelingenbeheer',
    titleBearerTokenManagement: 'Tokenbeheer',

    // misc
    loading: 'Laden...',
    from: 'Vanaf',
    to: 'Tot',
    searching: 'Aan het zoeken',
    search: 'Zoek',
    export: 'Exporteren',
    visualize: 'Visualiseren',
    download: 'Downloaden',
    select: 'Selecteren',
    cancel: 'Annuleren',
    noOptions: 'Geen opties',
    actions: 'Acties',
    department: 'Afdeling',
    createdAt: 'Aangemaakt op',
    lastUsed: 'Laatst gebruikt',
    createdBy: 'Aangemaakt door',
    important: 'Belangrijk',
    machine: 'Machine',
    copy: 'Kopiëren',
    close: 'Sluiten',
    delete: 'Verwijderen',
    remove: 'Verwijderen',
    name: 'Naam',
    date: 'Datum',
    create: 'Aanmaken',

    // Labels for landing screen
    homePickScreen: 'Kies een pagina',
    homeViewReports: 'Selecteer een scherm',
    homeBearerTokenManagement: 'Bearer-tokenbeheer',
    homeUserDepartmentManagement: 'Gebruikers en afdelingenbeheer',
    homeFileUpload: 'Handmatig bestand uploaden',

    // roles
    roleSuperAdmin: 'Superbeheerder',
    roleDepartmentAdmin: 'Afdelingsbeheerder',
    roleUser: 'Gebruiker',
    roleGuestUser: 'Gastgebruiker',

    // Reports overview
    reportsOverview: 'Rapportoverzicht',
    filterFiles: 'Bestanden filteren',
    searchByFilename: 'Filter op bestandsnaam',
    searchFilenameText: 'Bestanden zoeken...',
    searchByDepartment: 'Filter op afdeling',
    searchByHost: 'Filter op host',
    searchByDateRange: 'Zoeken binnen datumbereik',
    searchByBenchmark: 'Filter op benchmark',
    showNFiles: n => (n !== 1 ? `${n} bestanden weergegeven` : `${n} bestand weergegeven`),
    exportInProgress: 'Bezig met exporteren',

    aggregation: 'Aggregatie',
    noFilesSelected: 'Geen bestanden geselecteerd',
    selectedFiles: 'Geselecteerde bestanden',
    noMoreFilesToLoad: 'Geen bestanden meer om te laden',
    exportChooseAFormatToVisualize: 'Kies een formaat om te visualiseren',
    exportAgrregatePDF: 'Geaggregeerde PDF',
    exportAllPDF: 'Gebundelde PDF',

    // Manual file upload
    uploadDepartmentRequired: 'Selecteer een afdeling voordat u uploadt',
    uploadInvalidFileType: 'Upload een JSON-bestand',
    uploadLimitExceeded: 'U kunt slechts één bestand tegelijk uploaden. Probeer het opnieuw.',
    uploadFile: 'Bestand uploaden',
    dragAndDrop: 'Sleep een bestand hierheen of klik om uw JSON-bestand te uploaden.',
    dragAndDropShort: 'Sleep bestanden hierheen',
    orr: 'of',
    chooseFile: 'Kies bestand',
    selectDepartment: 'Selecteer een afdeling',
    selectDepartmentPlaceholder: 'Selecteer een afdeling',
    selectNoDepartment: 'Selecteer een afdeling',

    // Token Management
    tokenFailedFetch: 'Ophalen van bearertokens mislukt',
    errorFetchingTokens: 'Fout bij het ophalen van bearertokens',
    machineNameEmpty: 'Machinenaam mag niet leeg zijn',
    tokenCreatedSuccessfully: 'Bearer token succesvol aangemaakt',
    tokenFailedToCreate: 'Aanmaken van bearer token mislukt',
    errorCreatingToken: 'Fout bij het aanmaken van bearer-token',
    tokenRevokeConfirmation: 'Weet u zeker dat u dit token wilt intrekken? Deze actie kan niet ongedaan worden gemaakt.',
    tokenRevokedSuccessfully: 'Token succesvol ingetrokken',
    failedToRevokeToken: 'Intrekken van token mislukt',
    errorRevokingToken: 'Fout bij het intrekken van token',
    tokenCopied: 'Token gekopieerd naar klembord',
    tokenNotCopied: 'Kopiëren van token mislukt',

    createNewToken: 'Nieuw token aanmaken',
    machineName: 'Machinenaam',
    machineNamePlaceholder: 'bijv. Production Server 1',
    generateToken: 'Token genereren',
    usageInstructions: 'Gebruiksinstructies',
    usageInstructionsP1: 'Bearertokens stellen geautomatiseerde systemen in staat beoordelingsresultaten te uploaden.',
    usageInstructionsP2: 'Configureer uw .wrapper.env bestand met:',
    fakeURL: 'uw-domein.com',
    fakeToken: 'uw-token-hier',
    activeTokens: 'Actieve bearertokens',
    noActiveTokensForDepartment: 'Geen actieve tokens voor de geselecteerde afdeling.',
    revoke: 'Intrekken',

    tokenCreated: 'Bearer token aangemaakt',
    displayMsg: 'Dit token wordt slechts één keer getoond. Kopieer het nu.',

    // User management Dashboard
    depFailedFetch: 'Ophalen van afdelingen mislukt',
    errorFetchingDep: 'Fout bij het ophalen van afdelingen',
    usersFailedFetch: 'Ophalen van gebruikers mislukt',
    errorFetchingUsers: 'Fout bij het ophalen van gebruikers',
    depNameCannotBeEmpty: 'Afdelingsnaam mag niet leeg zijn',
    depCreatedSuccessfully: 'Afdeling succesvol aangemaakt',
    depFailedCreate: 'Aanmaken van afdeling mislukt',
    errorCreatingDep: 'Fout bij het aanmaken van afdeling',
    userHandleEmpty: 'Gebruikersnaam mag niet leeg zijn',
    userAddedToDepSuccess: 'Gebruiker succesvol aan afdeling toegevoegd',
    userFailedAddToDep: 'Toevoegen van gebruiker aan afdeling mislukt',
    errorAddUserToDep: 'Fout bij het toevoegen van gebruiker aan afdeling',
    userRemovedSuccess: 'Gebruiker succesvol uit afdeling verwijderd',
    userFailedRemoveFromDep: 'Verwijderen van gebruiker uit afdeling mislukt',
    errorRemovingUserFromDep: 'Fout bij het verwijderen van gebruiker uit afdeling',
    depRemovalConfirmation: 'Weet u zeker dat u deze afdeling wilt verwijderen? Dit verwijdert alle gekoppelde gebruikers.',
    depDeletedSuccess: 'Afdeling succesvol verwijderd',
    depFailedDelete: 'Verwijderen van afdeling mislukt',
    errorDeletingDep: 'Fout bij het verwijderen van afdeling',
    userDepartmentDashboard: 'Gebruikers en afdelingenbeheer',
    departmentManagement: 'Afdelingenbeheer',
    createNewDep: 'Nieuwe afdeling aanmaken',
    createDepPlaceholder: 'Afdelingsnaam',
    addUserToDep: 'Gebruiker aan afdeling toevoegen',
    userHandle: 'Gebruikersnaam',
    addUser: 'Gebruiker toevoegen',
    currentDepAssignments: 'Huidige afdelingskoppelingen',
    noDepMessage: 'Nog geen afdelingen aangemaakt. Maak uw eerste afdeling aan hierboven.',
    deleteDep: 'Afdeling verwijderen',
    noUsersAtDep: 'Geen gebruikers aan deze afdeling gekoppeld',
    removeUserFromDep: 'Gebruiker uit afdeling verwijderen',
    usersAssigned: num => (num !== 1 ? `${num} gebruikers gekoppeld` : `${num} gebruiker gekoppeld`),
  },
};

export default translations;
