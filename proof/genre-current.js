(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c3f4593bb86aebf5.js","sha256":"c3f4593bb86aebf56dd96ca9eee5cfe376646faccc6b8c5aaadfdb91ed4fef1a","count":244});
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
