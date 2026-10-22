(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.99ba84088343a414.js","sha256":"99ba84088343a4144fbae92a7b36d8dd215845ea5b99849d21a2252ddb70e8cb","count":244});
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
