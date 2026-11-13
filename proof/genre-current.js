(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.ae8454da40c89e3f.js","sha256":"ae8454da40c89e3fabdd7c9c80aa11fae69980107ef0dc8b20aeffd3c9555489","count":244});
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
