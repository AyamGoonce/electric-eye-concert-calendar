(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6b90779215c82867.js","sha256":"6b90779215c82867bdf424ff8c77aefab2eaf9f5931f959fa31fc606fd4c3ec4","count":244});
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
