(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b98027ffc24ef74f.js","sha256":"b98027ffc24ef74fcdb1ab7d33d4149c98f0270ffe97068c89eb3a4af0246740","count":207});
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
