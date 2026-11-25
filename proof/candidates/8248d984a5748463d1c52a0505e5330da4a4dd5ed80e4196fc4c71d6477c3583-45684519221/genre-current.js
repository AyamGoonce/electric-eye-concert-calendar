(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.a2941fcf5850c786.js","sha256":"a2941fcf5850c7862d7329087d3cfe1b828a9a3ee8ece1cb959317a321fc5b9c","count":244});
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
