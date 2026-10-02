(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.7b1e8da54f2489e8.js","sha256":"7b1e8da54f2489e8ffba38757bb34fc2d0172d9941ffb3bdff4a393ded8419a9","count":244});
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
