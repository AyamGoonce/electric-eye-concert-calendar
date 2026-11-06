(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.565df3b91c9bb339.js","sha256":"565df3b91c9bb339f3bbda6a5ef563291bd7ac105bb9e7e5341244e10c09857b","count":244});
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
