(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.6b0467a5f3e90ca5.js","sha256":"6b0467a5f3e90ca5c9942491feb8aa60191711bb885643eaa53dcf2c60af975d","count":244});
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
