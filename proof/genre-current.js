(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.544bfe7d36b5f24e.js","sha256":"544bfe7d36b5f24eb5945d9d07625d8081fc4b7f01fadc9172da189e05f299fc","count":244});
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
