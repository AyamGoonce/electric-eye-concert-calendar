(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.e3443f9fa874d4a0.js","sha256":"e3443f9fa874d4a0eec25263eafd7b1a1dab19581ca5811eaf8a3e4067769b2c","count":208});
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
