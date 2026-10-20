(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.b654629dbe0f374c.js","sha256":"b654629dbe0f374cbf1d02c45854d48faef2ddb14c11a595ee09d39d325f31eb","count":244});
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
