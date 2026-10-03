(function(){
  "use strict";
  var manifest = Object.freeze({"data":"venue-data.5f6bc52912bc435d.js","sha256":"5f6bc52912bc435dc5fcc22aa63700d4c047de5661e1f5cb007ba46f6381694d","count":169});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeVenueManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:venue-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:venue-data-error", {detail:{reason:"venue data unavailable"}}));
  };
  document.head.appendChild(script);
}());
