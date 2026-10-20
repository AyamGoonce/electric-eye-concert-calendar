(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.f31fe331cd01a155.js","sha256":"f31fe331cd01a155c79505ef1b1736e006924bf92a3f590f984bc09f43ba5a8c","count":244});
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
