(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.68498fa23ae6a920.js","sha256":"68498fa23ae6a92042cdc65ca4d1b386d9184bedb5af230bbe98b49b08145dcf","count":244});
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
