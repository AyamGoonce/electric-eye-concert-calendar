(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b03d9a0a394ca52b.js","sha256":"b03d9a0a394ca52b371bc0661bbdf045561037284f90f3cee8dc1c48c1c7fbd9","count":244});
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
