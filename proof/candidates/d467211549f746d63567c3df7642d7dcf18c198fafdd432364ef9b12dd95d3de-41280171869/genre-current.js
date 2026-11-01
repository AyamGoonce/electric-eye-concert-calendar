(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.428a72a952f329c0.js","sha256":"428a72a952f329c02a0c1176bc8206e5decbcfbda8d0565ddec01b17b5d78e56","count":244});
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
