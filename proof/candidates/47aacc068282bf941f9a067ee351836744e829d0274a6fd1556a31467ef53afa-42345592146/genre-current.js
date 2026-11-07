(function(){
  "use strict";
  var manifest = Object.freeze({"data":"genre-data.92dcf4e938e76413.js","sha256":"92dcf4e938e76413ad5975cb38eab1ffc0e65da2fc75a50cbc4c4b87df67f2d2","count":244});
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
