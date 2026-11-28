(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.93d0ed8ba646edc7.js","sha256":"93d0ed8ba646edc71a5deabadcd61eb838fe13543983dc53c67c8ebd1bd5f42f","count":244});
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
