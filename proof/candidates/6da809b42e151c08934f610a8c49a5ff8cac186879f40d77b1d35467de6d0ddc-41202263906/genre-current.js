(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.0e842a68ee718ffb.js","sha256":"0e842a68ee718ffb0ec9280095be968dfe65accaef8d12a5564358a9a9f3105e","count":244});
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
