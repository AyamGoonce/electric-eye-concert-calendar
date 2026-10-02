(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f0be13dcb6c359d8.js","sha256":"f0be13dcb6c359d8d142fc9b2e4ce46b44e639561b16b9aebd9fca4335283be2","count":247});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeGenreManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:genre-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:genre-data-error", {detail:{reason:"genre data unavailable"}}));
  };
  document.head.appendChild(script);
}());
