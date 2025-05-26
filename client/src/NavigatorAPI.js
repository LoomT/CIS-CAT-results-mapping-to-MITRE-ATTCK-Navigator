import AngularHook from './AngularHook.js';

export default class NavigatorAPI {
  constructor(targetWindow, layerURI, exportSVG) {
    this.targetGlobal = targetWindow;
    this.hooker = new AngularHook(targetWindow);

    this.layerURI = layerURI;
    this.exportSVG = exportSVG;
    this.dataTableComponent = null;
    this.setupHooks();
  }

  setupHooks() {
    let self = this;
    // Hook TabsComponent
    this.hooker.hook(
      ['newBlankTab', 'loadLayerFromURL'],
      'constructor',
      (instance) => {
        instance.loadLayerFromURL(self.layerURI.toString(), true)
          .then(() => {
            if (self.exportSVG && self.dataTableComponent) {
              self.dataTableComponent.exportRender();
            }
          });
      },
    );

    if (this.exportSVG) {
      // Hook DataTableComponent
      this.hooker.hook(
        ['exportRender'],
        'constructor',
        (instance) => {
          self.dataTableComponent = instance;
        },
      );

      // Hook SVGExportComponent
      this.hooker.hook(
        ['downloadSVG'],
        'buildSVG',
        (instance) => {
          try {
            instance.downloadSVG();
          }
          catch {
            // This might happen when debouncing, in that case buildSVG will be called again and we should be good
          }
        },
      );

      this.hooker.hook(
        ['promptNavAway'],
        'promptNavAway',
        (instance, args) => {
          try {
            instance.configService.setFeature('leave_site_dialog');
            /* This is required to get rid of the unsaved changes popup */
            args[0].returnValue = '';
          }
          catch {
          }
        },
      );
    }
  }
}
