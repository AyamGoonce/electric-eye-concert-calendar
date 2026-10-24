(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.161f9fe67ddd69a5.js","sha256":"161f9fe67ddd69a56331ebc968e8446a52652fb1beae5860ac90aa39acaa1a96","count":244});
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
