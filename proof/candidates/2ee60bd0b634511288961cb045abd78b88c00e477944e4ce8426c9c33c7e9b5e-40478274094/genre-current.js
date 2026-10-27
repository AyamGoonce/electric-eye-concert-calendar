(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7e972c3ad4d4f2de.js","sha256":"7e972c3ad4d4f2dea2edfcd06f24725384157e58cf1adc82e71443bc05a69078","count":244});
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
