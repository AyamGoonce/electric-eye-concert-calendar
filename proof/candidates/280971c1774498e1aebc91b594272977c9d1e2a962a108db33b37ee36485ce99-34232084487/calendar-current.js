(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.280971c1774498e1.js","sha256":"280971c1774498e1aebc91b594272977c9d1e2a962a108db33b37ee36485ce99","count":2479,"publishedAt":"2026-09-08T13:30:51Z","state":"calendar-state.json","stateSha256":"b6be7ce4863d4f917ae0a8533722965a878de9442bfe1f80efc20e71333aee3b"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
