(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.320c18546d5577b6.js","sha256":"320c18546d5577b683bd5cc32792aa7aca98dd99f4d59f584123ae1f74a9b0a2","count":244});
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
