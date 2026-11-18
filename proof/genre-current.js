(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c7a6eb41e22e914a.js","sha256":"c7a6eb41e22e914a48d6bc11776eb55b1c89dac137e98e84ac96a24c16d013cd","count":244});
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
