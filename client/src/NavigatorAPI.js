import AngularHook from './AngularHook.js';

export default class NavigatorAPI {
  constructor(targetWindow, layerURI) {
    this.targetGlobal = targetWindow;
    this.hooker = new AngularHook(targetWindow);

    this.layerURI = layerURI;
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
            if (self.dataTableComponent) {
              self.dataTableComponent.exportRender();
            }
          });
      },
    );

    // Hook DataTableComponent
    this.hooker.hook(
      ['exportRender'],
      'ngAfterViewInit',
      (instance) => {
        self.dataTableComponent = instance;
        // self.dataTableComponent.exportRender();
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

  async downloadSVG() {
    return new Promise((resolve, reject) => {
      // Hook SVGExportComponent
      this.hooker.hook(
        ['downloadSVG'],
        'buildSVG',
        (instance) => {
          try {
            instance.downloadSVG();
            resolve(null);
          }
          catch {
            // This might happen when debouncing, in that case buildSVG will be called again and we should be good
          }
        },
      );
    });
  }

  async getSVG() {
    let self = this;

    return new Promise((resolve, reject) => {
      // Hook SVGExportComponent
      this.hooker.hook(
        ['downloadSVG'],
        'buildSVG',
        (instance) => {
          try {
            let svgElement = self.targetGlobal.document.getElementById('svg' + instance.viewModel.uid);
            if (svgElement != null) {
              svgElement.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
              resolve(svgElement);
            }
          }
          catch {
            // This might happen when debouncing, in that case buildSVG will be called again and we should be good
          }
        },
      );
    });
  }
}
