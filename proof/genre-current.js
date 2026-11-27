(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.c30853f54cc2ae44.js","sha256":"c30853f54cc2ae44074a1cf9bf8255f3cdc210ca636694445152824ba0c11972","count":244});
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
