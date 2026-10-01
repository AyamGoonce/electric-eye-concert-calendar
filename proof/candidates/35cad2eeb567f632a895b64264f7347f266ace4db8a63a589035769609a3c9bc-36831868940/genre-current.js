(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.86c812d7dbe75981.js","sha256":"86c812d7dbe7598125971028d34833b0095d2a545c30dc6707a314bd6ff252c3","count":208});
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
